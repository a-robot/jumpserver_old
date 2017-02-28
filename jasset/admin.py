from django.contrib import admin

from .models import AssetGroup, IDC, Asset, AssetRecord, AssetAlias


admin.site.register(AssetGroup)
admin.site.register(IDC)
admin.site.register(Asset)
admin.site.register(AssetRecord)
admin.site.register(AssetAlias)
