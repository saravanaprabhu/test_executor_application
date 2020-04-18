# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Request, Requester, Test , Template
# Register your models here.

admin.site.register(Requester)
admin.site.register(Request)
admin.site.register(Test)
admin.site.register(Template)

