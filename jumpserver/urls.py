from django.conf.urls import include, url
from django.contrib import admin

from jumpserver.views import index, skin_config, jmp_login, jmp_logout, exec_cmd, upload, download, web_terminal


urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^admin/', admin.site.urls),
    url(r'^skin_config/$', skin_config, name='skin_config'),
    url(r'^login/$', jmp_login, name='login'),
    url(r'^logout/$', jmp_logout, name='logout'),
    url(r'^exec_cmd/$', exec_cmd, name='exec_cmd'),
    url(r'^file/upload/$', upload, name='file_upload'),
    url(r'^file/download/$', download, name='file_download'),
    url(r'^terminal/$', web_terminal, name='terminal'),
    url(r'^jsetting/', include('jsetting.urls')),
    url(r'^juser/', include('juser.urls')),
    url(r'^jasset/', include('jasset.urls')),
    url(r'^jlog/', include('jlog.urls')),
    url(r'^jperm/', include('jperm.urls')),
    url(r'^jproject/', include('jproject.urls')),
]
