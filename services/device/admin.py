from django.contrib import admin

from device.models import Device


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        "user_id", "platform_id", "name",
        "registered_at", "last_login",
    )
    search_fields = ("user_id", "platform_id", "name")
