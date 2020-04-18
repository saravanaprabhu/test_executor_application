from __future__ import unicode_literals

import requests
from .models import Request ,Test
from rq import get_current_job
from django_rq import job
from django.shortcuts import get_object_or_404
import time
import random
from celery import shared_task

#arr = [False]*100 #need to change if number of env IDs increase

def testcase1():
    num = random.randint(1,180)
    if num % 2 == 0:
        time.sleep(num/2)
        return 0
    else:
        time.sleep(num/2)
        return 1

@shared_task
def run_test(reqid):
    print reqid
    req_inst = get_object_or_404(Request,pk=reqid)
    #global arr
    while True:
        test_system = get_object_or_404(Test, pk=req_inst.test_details.test_env_id)
        #print req_inst.test_details.system_status
        #print test_system.system_status
        if not test_system.system_status and req_inst.test_status == 'Queued':
            #req_inst.test_details.system_status = True
            req_inst.test_status = 'Running'
            req_inst.save()
            test_system.system_status = True
            test_system.save()
            if testcase1() == 1:
                req_inst.test_status = 'Failed'
                req_inst.save()
                test_system.system_status = False
                test_system.save()
                print test_system.system_status
                return 1
            else:
                req_inst.test_status = 'Passed'
                #req_inst.test_details.system_status = False
                req_inst.save()
                test_system.system_status = False
                test_system.save()
                print test_system.system_status
                #print "5", arr
                #arr[int(req_inst.test_details.test_env_id)] = False
                #print "6", arr
                return 0
        else:
            continue




