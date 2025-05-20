from django.contrib import admin
from idvalid_core.admin import ShadowAdmin
from tenant import models


@admin.register(models.User)
class UserAdmin(ShadowAdmin):
    pass


@admin.register(models.Tenant)
class TenantAdmin(admin.ModelAdmin):
    pass


@admin.register(models.TenantUser)
class TenantUserAdmin(admin.ModelAdmin):
    pass
