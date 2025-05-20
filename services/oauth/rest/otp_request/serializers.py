from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

if TYPE_CHECKING:
    from oauth.models import OtpRequest


logger = logging.getLogger(__name__)
__all__ = ("VerifySerializer",)


class VerifySerializer(serializers.Serializer):
    default_error_messages = {
        "otp_invalid": _("Invalid."),
        "otp_expired": _("Expired."),
    }
    otp = serializers.CharField(
        max_length=6, min_length=6)

    def validate_otp(self, value):
        instance = self.instance  # type: OtpRequest
        if instance.otp != value:
            self.fail("otp_invalid")
        elif not instance.is_alive():
            self.fail("otp_expired")
        return value
