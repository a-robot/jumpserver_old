import json

from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render

from jumpserver.api import my_render, require_role
from jasset.models import Asset, ASSET_TYPE, ASSET_STATUS, ASSET_ENV
from jproject.models import Project


@require_role('user')
def project_list(request):
    return my_render('jproject/project_list.html', locals(), request)


@require_role('user')
def project_list_json(request):
    assets = Asset.objects.all()
    ret = {}
    for asset in assets:
        if asset.project:
            pn = asset.project.project_name
        else:
            pn = ''

        ret_project = ret.get(pn, {})
        ret_assets = ret_project.get('assets', [])
        ret_asset = {
            'id': asset.id,
            'ip': asset.ip,
            'other_ip': asset.other_ip,
            'hostname': asset.hostname,
            'username': asset.username,
            'idc': asset.idc,
            'mac': asset.mac,
            'remote_ip': asset.remote_ip,
            'brand': asset.brand,
            'cpu': asset.cpu,
            'memory': asset.memory,
            'disk': asset.disk,
            'system_type': asset.system_type,
            'system_version': asset.system_version,
            'system_arch': asset.system_arch,
            'position': asset.position,
            'number': asset.number,
            'env': dict(ASSET_ENV).get(asset.env, ''),
            'status': dict(ASSET_STATUS).get(asset.status, ''),
            'asset_type': dict(ASSET_TYPE).get(asset.asset_type, ''),
            'is_active': asset.is_active,
            'comment': asset.comment,
        }

        ret_asset['project_name'] = pn
        ret_assets.append(ret_asset)
        ret_project['assets'] = ret_assets
        ret[pn] = ret_project

    json_data = json.dumps(ret)
    return HttpResponse(json_data)
