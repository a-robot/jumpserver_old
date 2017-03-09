import json

from jasset.models import Asset, ASSET_TYPE, ASSET_STATUS, ASSET_ENV
from jproject.models import Project, AppModule
from jumpserver.api import require_role


def get_app_modules(project_id, perm_asset_ids):
    ret = []
    project = Project.objects.filter(id=project_id)[0]
    app_modules = project.appmodule_set.all()
    for app_module in app_modules:
        hosts = get_hosts(app_module.id, perm_asset_ids)
        if len(hosts) == 0:
            continue

        ret_app_module = {}
        ret_app_module['name'] = app_module.app_module_name
        ret_app_module['hosts'] = hosts
        ret.append(ret_app_module)

    return ret


def get_hosts(app_module_id, perm_asset_ids):
    ret = []
    app_module = AppModule.objects.filter(id=app_module_id)[0]
    assets = app_module.asset_set.filter(pk__in=perm_asset_ids)

    for asset in assets:
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
            'disk': disk_format(asset.disk),
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
        ret.append(ret_asset)

    return ret


def disk_format(disk):
    if not disk:
        return disk

    disk_obj = json.loads(disk)
    ret = ''
    for name, size in disk_obj.items():
        ret += '%s: %sG, ' % (name, size)
    ret = ret.rstrip(', ')
    return ret
