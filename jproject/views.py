import json

from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render

from jumpserver.api import my_render, require_role
from jproject.models import Project
from jproject.project_api import get_app_modules


@require_role('user')
def project_list(request):
    return my_render('jproject/project_list.html', locals(), request)


@require_role('user')
def project_list_json(request):
    '''
    return data format:
    ret = {
        'projects': [
            {
                'name': 'project_name',
                'app_modules': [
                    {
                        'name': 'module_name',
                        'hosts': [
                            {
                                'name': 'host_name',
                                'ip': 'ip',
                                '...': '...'
                            }
                        ]
                    }
                ]
            },
        ]
    }
    '''
    ret = {}
    ret['projects'] = []

    projects = Project.objects.all()
    for project in projects:
        ret_project = {}
        ret_project['name'] = project.project_name
        ret_project['app_modules'] = get_app_modules(project.id)
        ret['projects'].append(ret_project)

    json_data = json.dumps(ret)
    return HttpResponse(json_data)
