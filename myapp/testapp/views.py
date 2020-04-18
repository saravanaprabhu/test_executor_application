# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect, get_object_or_404
# Create your views here.
from .models import Request, Requester, Test ,Template
from .forms import TestForm
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response

from serializers import  RequestSerializer


def home(request):

    tests = Request.objects.order_by('-created')
    page = request.GET.get('page', 1)

    paginator = Paginator(tests, 10)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    return render(request,'home.html', {'all_tests': users})

def get_test_details(request, pk):
    test = get_object_or_404(Test, pk=pk)
    return render(request,'test_status.html',{'test_result': test})

def get_test_status(request,pk):
    test_state = get_object_or_404(Request, pk=pk)
    return render(request,'test_state.html',{'test_status': test_state})


def start_new_test(request,status_dict={}):

    if request.method == "POST":
        form = TestForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            ret = Request.objects.create(created= timezone.now(),template = form.cleaned_data.get('template'),username = form.cleaned_data.get('username'),
                                         test_details = form.cleaned_data.get('test_details'),test_status='Queued')
            #print "*****taskentry*****", arr
            #run_test.delay(ret.req_id)
            #run_test.delay(ret.created, ret.template.template_name, ret.username , ret.test_details.test_env_id, ret.test_status)
            status_dict['status'] = 'Success'
            return redirect('home')
    else:
        form = TestForm()
        return render(request,'start_test.html', {'form': form})

class StartTestAPI(APIView):

    def post(self,request,format=None):
        #test_environment_id = request.POST.get('test_env_id')
        #username = request.POST.get('username')
        #test_template_name = request.POST.get('template')
        status_dict = {}
        #print request.POST.get('template')
        #print request.POST.get('test_details')
        request.POST._mutable = True

        #request.POST = request.POST.copy()
        #print request.POST.get('username')
        params = {}
        requester = Requester.objects.filter(username=request.POST.get('username'))
        if len(requester) > 0:
            params['username'] = requester[0].id
        else:
            return Response("\nUser not found", status=404)
        template_id = Template.objects.filter(template_name=request.POST.get('template'))
        if len(template_id)  > 0:
            params['template'] = template_id[0].id
        else:
            return Response("\nTest Template Not found", status=404)
        #TODO Compare the Test Environment ID also
        request.POST.update(params)

        response = start_new_test(request,status_dict)
        if 'status' in status_dict:
            return HttpResponse("\nSuccessfully Started a new test.\nTest will start running when the test environment is available")
        else:
            return Response("\nCreation of new test failed",status=404)




class GetTestStatus(APIView):
    def get(self,request,pk=-1):
        if pk == -1:
            request_list= Request.objects.all()
            serializer = RequestSerializer(request_list,many=True)
            return Response(serializer.data)
        else:
            #req_obj = get_object_or_404(Request,pk=pk)
            req_obj = Request.objects.filter(req_id=pk)

            if req_obj != None:
                serializer = RequestSerializer(req_obj, many=True)
                return Response(serializer.data)
            else:
                return Response("\nRequest Not Found", status=404)



