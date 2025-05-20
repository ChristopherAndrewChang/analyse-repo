from __future__ import annotations
from typing import TYPE_CHECKING

from django.contrib import admin

if TYPE_CHECKING:
    pass


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "user_id", "client_type", "authorization_grant_type")
    list_filter = ("client_type", "authorization_grant_type", "skip_authorization")
    radio_fields = {
        "client_type": admin.HORIZONTAL,
        "authorization_grant_type": admin.VERTICAL,
    }
    search_fields = ("name",)
    # raw_id_fields = ("user",)


class AccessTokenAdmin(admin.ModelAdmin):
    list_display = ("token", "user_id", "application", "expires")
    list_select_related = ("application",)
    raw_id_fields = ("source_refresh_token",)
    search_fields = ("token",)
    list_filter = ("application",)


class GrantAdmin(admin.ModelAdmin):
    list_display = ("code", "application", "user_id", "expires")
    # raw_id_fields = ("user",)
    search_fields = ("code",)


class IDTokenAdmin(admin.ModelAdmin):
    list_display = ("jti", "application", "expires")
    # raw_id_fields = ("user",)
    search_fields = ()
    list_filter = ("application",)
    list_select_related = ("application",)


class RefreshTokenAdmin(admin.ModelAdmin):
    list_display = ("token", "user_id", "application")
    raw_id_fields = ("access_token",)
    search_fields = ("token",)
    list_filter = ("application",)
