from __future__ import annotations
from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _

from rest_framework.permissions import BasePermission

if TYPE_CHECKING:
    from rest_framework.request import Request
    from account.models import Enrollment


__all__ = ("CreateAccountPermission",)


class CreateAccountPermission(BasePermission):
    default_messages = {
        "expired": _("Token expired."),
        "invalid_device": _("Invalid device."),
        "invalid_agent": _("Invalid agent."),
    }
    message: str
    code: str

    def set_error_detail(self, code: str):
        self.message = self.default_messages[code]
        self.code = code

    def has_object_permission(
            self, request: Request, view, obj: Enrollment) -> bool:
        if obj.otp_token.is_expired():
            self.set_error_detail("expired")
            return False
        if request.COOKIES.get("device_id") != obj.device_id:
            self.set_error_detail("invalid_device")
            return False
        if request.headers["User-Agent"] != obj.user_agent:
            self.set_error_detail("invalid_agent")
            return False
        return True
