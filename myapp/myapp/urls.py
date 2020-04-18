"""myapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url , include
from django.contrib import admin
from testapp.services import process_queue

from testapp import views


urlpatterns = [
    url(r'^$',views.home,name="home"),
    url(r'^start_test/',views.start_new_test,name="start_test"),
    url(r'^test/(?P<pk>\d+)/$', views.get_test_details, name='get_test_details'),
    url(r'^request/(?P<pk>\d+)/$', views.get_test_status, name='get_test_status'),
    url(r'^admin/', admin.site.urls),
    url(r'^process/queue/$', process_queue),
    url(r'^start_test_api/$',views.StartTestAPI.as_view()),
    url(r'^get_test_status/(?P<pk>\d+)/$',views.GetTestStatus.as_view()),
]
