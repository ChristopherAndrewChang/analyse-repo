from __future__ import annotations
from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import BasePermission as drf_BasePermission

if TYPE_CHECKING:
    from typing import TypeVar
    from rest_framework.request import Request
    from rest_framework.views import APIView

    ViewType = TypeVar("ViewType", bound=APIView)


__all__ = ("BasePermission", "DeviceCookieRequired")


class BasePermission(drf_BasePermission):
    error_messages = {}  # type: dict[str, str]
    message: str
    code: str

    def set_error_detail(self, code: str, **kwargs):
        # noinspection StrFormat
        self.message = self.error_messages[code].format(**kwargs)
        self.code = code


class DeviceCookieRequired(BasePermission):
    message = _("missing `device_id` cookies")
    code = "missing_cookies"

    def has_permission(self, request: Request, view: "ViewType") -> bool:
        try:
            request.COOKIES["device_id"]
        except KeyError:
            return False
        return True
