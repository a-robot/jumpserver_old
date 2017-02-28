# coding=utf-8
from django.conf.urls import include, url

from jproject.views import project_list, project_list_json


urlpatterns = [
    url(r'^project/list/$', project_list, name='project_list'),
    url(r'^project/list/json$', project_list_json, name='project_list_json'),
]
