from django.contrib import admin
from authn import models


@admin.register(models.TOTPDevice)
class TOTPDeviceAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Platform)
class PlatformAdmin(admin.ModelAdmin):
    pass


@admin.register(models.TOTP)
class TOTPAdmin(admin.ModelAdmin):
    pass
