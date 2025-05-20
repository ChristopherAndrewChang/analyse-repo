from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.utils.translation import gettext_lazy as _

from rest_framework.permissions import BasePermission

if TYPE_CHECKING:
    from rest_framework.request import Request
    from otp.models import Code
    from .views import CodeView


logger = logging.getLogger(__name__)
__all__ = ("ActiveCodePermission",)


class ActiveCodePermission(BasePermission):
    default_messages = {
        "expired": _("Code expired."),
        "invalid_device": _("Invalid device."),
    }
    message: str
    code: str

    def set_error_detail(self, code: str):
        self.message = self.default_messages[code]
        self.code = code

    def has_object_permission(
            self, request: Request, view: CodeView, obj: Code) -> bool:
        if obj.is_expired():
            self.set_error_detail("expired")
            return False
        if request.COOKIES.get("device_id") != obj.device_id:
            self.set_error_detail("invalid_device")
            return False
        return True
