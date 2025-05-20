from __future__ import annotations
from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _

from rest_framework.permissions import BasePermission

from device.models import Device

if TYPE_CHECKING:
    from typing import TypeVar
    from rest_framework.request import Request
    from rest_framework.views import APIView

    ViewType = TypeVar("ViewType", bound=APIView)


__all__ = ("DeviceRegisteredPermission",)


class DeviceRegisteredPermission(BasePermission):
    default_messages = {
        "missing_cookies": _("Missing `device_id` cookies."),
        "device_not_registered": _("Invalid device not registered."),
    }
    message: str
    code: str

    def set_error_detail(self, code: str):
        self.message = self.default_messages[code]
        self.code = code

    def has_permission(self, request: Request, view: "ViewType") -> bool:
        try:
            device_id = request.COOKIES["device_id"]
        except KeyError:
            self.set_error_detail("missing_cookies")
            return False

        try:
            request.device = Device.objects.get(
                user_id=request.user.id,
                device_id=device_id)
        except Device.DoesNotExist:
            self.set_error_detail("device_not_registered")
            return False
        return True
