#!/usr/bin/python
#
# Copyright (c) 2014, Oracle and/or its affiliates. All rights reserved.
#

import errno, urllib2, ctypes, sys, os, time, atexit, signal, ssl
from ctypes import *

class Daemon:

	def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null',
					stderr='/dev/null', foreground=False):
		self.stdin = stdin
		self.stdout = stdout
		self.stderr = stderr
		self.pidfile = pidfile
		self.foreground = foreground
		self.force_stop = False
		self.ssl_context = ssl._create_unverified_context()

		signal.signal(signal.SIGTERM, self.graceful_shutdown)

	'''	
	def graceful_shutdown(self, num=None, stack=None):
		try:
			urllib2.urlopen('https://localhost:8000/services/sched/stopped/', context=self.ssl_context)
		except urllib2.URLError, e:
			pass
		sys.exit(0)
	'''

	def daemonize(self):
		"""
		Create the daemon process, decouple from the parent and redirect the filehandles.
		"""

		if self.foreground:
			return

		for i in range(2):
			# double fork, after the first fork, chdir and set the sid, unset any umask
			# once decoupled, fork again, exit and continue execution
			try:
				pid = os.fork()
				if pid > 0:
                    sys.exit(0)
            except OSError, e:
                sys.stderr.write("fork %d failed: %d (%s)\n" % (i, e.errno, e.strerror))
                sys.exit(1)

			# decouple from parent environment
			if not i:
				os.chdir("/")
				os.setsid()
				os.umask(0)

		sys.stdout.flush()
		sys.stderr.flush()
		si = file(self.stdin, 'r')
		so = file(self.stdout, 'a+')
		se = file(self.stderr, 'a+', 0)
		# redirect in, out, err
		for sfn, tfn in ( (si, sys.stdin),
				(so, sys.stdout),
				(se, sys.stderr)):
			os.dup2(sfn.fileno(), tfn.fileno())
		self.writepid()

	def writepid(self):
		# register the exit handler to delete the pid file
		atexit.register(self.delete_pid_file)

		# get the pid and write it to our pid file
		pid = str(os.getpid())
		#with file(self.pidfile,'w+') as pfile:
		with os.fdopen(os.open(self.pidfile, os.O_WRONLY | os.O_CREAT, 0600), 'w') as pfile:
			pfile.write("%s\n" % pid)

	def delete_pid_file(self):
		"""
		Delete the PID file
		"""
		os.remove(self.pidfile)

	def start(self):
		"""
		Start the Daemon
		"""
		# Check for a pid file to see if the daemon already runs
		try:
			with file(self.pidfile,'r') as pf:
				pid = int(pf.read().strip())
		except IOError:
			pid = None

		if pid:
			message = ''
			try:
				message = "pid file %s exists and pid %s is valid. Daemon is running.\n" % (self.pidfile, pid)
				os.kill(pid, 0)
			except OSError, e:
				if e.errno == errno.ESRCH:
					message = "pid file %s exists but process %s not running.\n" % (self.pidfile, pid)
				elif e.errno == errno.EPERM:
					message = "Permission denied.\n"

			sys.stderr.write(message)
			sys.exit(1)
        '''
		try:
			urllib2.urlopen('https://localhost:8000/services/sched/started/',context=self.ssl_context)
		except urllib2.URLError, e:
			# Conn refused or the like, retry later
			sys.stderr.write('Error communicating with SVA. Is SVA Running?\n')
			sys.stderr.write('%s\n' % e)
			sys.exit(1)
        '''
        if not self.foreground:
            self.daemonize()

        self.run()

	def stop(self):
		"""
		Stop the daemon
		"""
		# Get the pid from the pidfile
		if self.foreground:
			sys.exit(0)
		try:
			pf = file(self.pidfile,'r')
			pid = int(pf.read().strip())
			pf.close()
		except IOError:
			pid = None

		if not pid:
			message = "pidfile %s does not exist. Daemon not running?\n"
			sys.stderr.write(message % self.pidfile)
			return

		try:
			# If we want to pull the rug out from underneath, send SIGKILL
			if self.force_stop:
				os.kill(pid, signal.SIGKILL)
				self.delete_pid_file()
			else:
				# This will trigger the signal handler, which will either
				# be queued, or will fire straight away, depending on
				# whether the daemon is in the middle of a deployment.
				os.kill(pid, signal.SIGTERM)

		except OSError, err:
			if err.errno == errno.ESRCH:
				if os.path.exists(self.pidfile):
					os.remove(self.pidfile)
			else:
				if  err.errno == errno.EPERM:
					message = "Permission denied.\n"
					sys.stderr.write(message)
				else:
					sys.stderr.write(str(err))

	def restart(self):
		"""
		Restart the daemon
		"""
		self.stop()
		self.start()

	def marshall_signals(self, block=True):
		'''
		Python has no direct exposure of sigprocmask, which is
		required to enable signals to be queued for processing.

		We need a way to block whilst IO Domains are physically being
		deployed.

		This is explicitely listed as unsupported in python due to a lack of
		support at an OS level for sigprocmask. However, Solaris has sigprocmask
		so we are good to go.

		Create a C-array called 'sigs'. Populate this array based
		on the block parameter.

		If block:
			we want to create a blocking mask for SIGTERM
		if not block:
			we want to undo the blocking mask for SIGTERM

		To do this, we emulate the SIGSET Structure
		and into an instance we place the signals we wish
		to block (either SIGTERM, or None).

		libc is then loaded to provide access to sigprocmask.

		Finally, call sigprocmask, passing it 3 (SIG_SETMASK),
		the SIGSET variable 'mask', we pass None as the oset
		value, since we aren't fussed about restoring any
		signal set after.

		'''
		SIGSET_NWORDS = 1024 / (8 * sizeof(c_ulong))
		SIG_SETMASK = 3
		class SIGSET(Structure):
			_fields_ = [
				('val', c_ulong * SIGSET_NWORDS)
		    ]

		sigs = (c_ulong * SIGSET_NWORDS)()
		if block:
			sigs[0] = 2 ** (signal.SIGTERM - 1)

		mask = SIGSET(sigs)
		libc = ctypes.cdll.LoadLibrary("libc.so")
		libc.sigprocmask(SIG_SETMASK, pointer(mask), None)
    '''
	def computer_says_no(self):
		try:
			# Check whether the daemon is in a deployment phase
			returned = urllib2.urlopen('https://localhost:8000/services/sched/deploying/', context=self.ssl_context)
			res = returned.read()
			
			if res.strip().lower() == 'true':
				return True
			else:
				return False
		
		except urllib2.URLError, e:
			raise e
    '''
	def run(self):
		"""
		To be overridden in subclass
		"""


class PyDaemon(Daemon):
    def run(self):
        while True:
            # block SIGTERM whilst this block is running
			self.marshall_signals(block=True)
            try:
		        # tell SVA to start processing the queue.
				# this can take several minutes to return
				urllib2.urlopen('https://localhost:8000/queue/process/', context=self.ssl_context)
			except urllib2.URLError:
				# Conn refused or the like, retry later
				# but first unblock the SIGTERM so that we can
				# receive a kill signal
				self.marshall_signals(block=False)
				time.sleep(10)
				continue

			# the hard work is done for now, unblock signals and rest
			self.marshall_signals(block=False)
			time.sleep(10)

if __name__ == "__main__":
	daemon = PyDaemon('/tmp/iodctqd.pid')
	if len(sys.argv) == 2 and sys.argv[1] != '-h':
		dfunc = None
		if 'start' == sys.argv[1]:

			dfunc = daemon.start
        '''
		elif 'check' == sys.argv[1]:
			print 'Checking with SVA whether daemon is in a deployment phase'
			try:
				if daemon.computer_says_no():
					print 'Server is in a deployment phase, please wait before shutting down'
					sys.exit(0)
				else:
					print 'Server is safe to stop'
					sys.exit(0)
			except urllib2.URLError, e:
				sys.stderr.write('Error communicating with SVA. Is SVA Running?\n')
				sys.stderr.write('%s\n' % e)
				sys.exit(1)
        '''
		elif 'stop' == sys.argv[1]:
			dfunc = daemon.stop
		elif 'graceful-stop' == sys.argv[1]:
			dfunc = daemon.stop
		elif 'force-stop' == sys.argv[1]:
			daemon.force_stop = True
			dfunc = daemon.stop
		elif 'restart' == sys.argv[1]:
			dfunc = daemon.restart
		elif 'foreground' == sys.argv[1]:
			dfunc = daemon.start
			daemon.foreground = True
		else:
			print "Unknown command"
			sys.exit(2)

		try:
			dfunc()
		except KeyboardInterrupt:
			daemon.graceful_shutdown()
			print '\nCtrl-C, Exiting.'

		sys.exit(0)
	else:
		print "usage: %s check|start|stop|force-stop|restart|foreground" % sys.argv[0]
		sys.exit(2)
