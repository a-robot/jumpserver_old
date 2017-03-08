import json

from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render

from jasset.asset_api import get_assets_by_username
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
    username = request.user.username
    perm_assets = get_assets_by_username(username)
    perm_asset_ids = []
    for asset in perm_assets:
        perm_asset_ids.append(asset.id)

    for project in projects:
        app_modules = get_app_modules(project.id, perm_asset_ids)
        if len(app_modules) == 0:
            continue

        ret_project = {}
        ret_project['name'] = project.project_name
        ret_project['app_modules'] = app_modules
        ret['projects'].append(ret_project)

    json_data = json.dumps(ret)
    return HttpResponse(json_data)
