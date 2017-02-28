from django.contrib import admin

from .models import PermLog, PermSudo, PermRole, PermRule, PermPush


admin.site.register(PermLog)
admin.site.register(PermSudo)
admin.site.register(PermRole)
admin.site.register(PermRule)
admin.site.register(PermPush)
