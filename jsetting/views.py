import os

from django.shortcuts import render
from django.conf import settings

from jsetting.models import Setting
from jumpserver.api import require_role, get_object, ServerError, mkdir, CRYPTOR


@require_role('admin')
def setting(request):
    header_title, path1 = '项目设置', '设置'
    setting_default = get_object(Setting, name='default')

    if request.method == "POST":
        try:
            setting_raw = request.POST.get('setting', '')
            if setting_raw == 'default':
                username = request.POST.get('username', '')
                port = request.POST.get('port', '')
                password = request.POST.get('password', '')
                private_key = request.POST.get('key', '')

                if len(password) > 30:
                    raise ServerError('秘密长度不能超过30位!')

                if '' in [username, port]:
                    return ServerError('所填内容不能为空, 且密码和私钥填一个')
                else:
                    private_key_dir = os.path.join(settings.BASE_DIR, 'keys', 'default')
                    private_key_path = os.path.join(private_key_dir, 'admin_user.pem')
                    mkdir(private_key_dir)

                    if private_key:
                        with open(private_key_path, 'w') as f:
                                f.write(private_key)
                        os.chmod(private_key_path, 0o600)

                    if setting_default:
                        if password:
                            password_encode = CRYPTOR.encrypt(password)
                        else:
                            password_encode = password
                        Setting.objects.filter(name='default').update(field1=username, field2=port,
                                                                      field3=password_encode,
                                                                      field4=private_key_path)

                    else:
                        password_encode = CRYPTOR.encrypt(password)
                        setting_r = Setting(name='default', field1=username, field2=port,
                                            field3=password_encode,
                                            field4=private_key_path).save()
                        msg = "设置成功"
        except ServerError as e:
            error = e.message
    return render(request, 'setting.html', locals())
