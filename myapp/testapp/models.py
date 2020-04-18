# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.


class Requester(models.Model):
    username = models.CharField(max_length=100)

    def __str__(self):
        return self.username

class Test(models.Model):
    #TODO : Make test_env_id accepts only values between 1 to 100
    #Because declared the size of boolean array as 100
    test_env_id = models.AutoField(primary_key=True)
    system_status = models.BooleanField(default=False)

    def __str__(self):
        return str(self.test_env_id)

class Template(models.Model):
    template_name = models.CharField(max_length=500)

    def __str__(self):
        return self.template_name

class Request(models.Model):
    req_id = models.AutoField(primary_key=True)
    created = models.DateTimeField(null=True)
    username = models.ForeignKey(Requester,on_delete=models.CASCADE)
    test_details = models.ForeignKey(Test,on_delete=models.CASCADE)
    template = models.ForeignKey(Template,on_delete=models.CASCADE)
    test_status = models.CharField(max_length=10) #Running, failed, Success , Queued




