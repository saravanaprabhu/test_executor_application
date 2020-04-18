from __future__ import unicode_literals

from django.http import HttpResponse
from .models import Request, Test
from tasks import run_test


def process_queue(request):
    idle_machines = Test.objects.filter(system_status=False)
    string = ""
    if idle_machines == None:
        return HttpResponse('There are no Idle machines at this time')
    else:
        print idle_machines
        for machine in idle_machines:
            print machine
            queued_entries = Request.objects.filter(test_details=machine.test_env_id).filter(test_status='Queued').order_by('created')
            if queued_entries.exists():
                run_test.delay(queued_entries[0].req_id)

    success = HttpResponse('Scheduled waiting Tasks' + string )
    return success


