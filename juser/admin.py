from django.contrib import admin

from .models import UserGroup, User, AdminGroup, Document


admin.site.register(UserGroup)
admin.site.register(User)
admin.site.register(AdminGroup)
admin.site.register(Document)
