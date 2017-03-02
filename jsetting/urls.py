# coding=utf-8

from django.conf.urls import url

from jsetting.views import setting


urlpatterns = [
    url(r'^setting/$', setting, name='setting'),
]
