from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from account.models import constants, Enrollment, Email
from account.settings import account_settings

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "CreateSerializer",
)


class CreateSerializer(serializers.Serializer):
    default_error_messages = {
        "email_registered": _("Already registered."),
        "otp_already_sent": _(
            f"OTP already sent to this email. Try again "
            f"in {account_settings.DEFAULT_ENROLLMENT_PIN_RESEND} seconds.")
    }

    email = serializers.EmailField(
        write_only=True)
    state = serializers.CharField(
        write_only=True,
        max_length=constants.ENROLLMENT_STATE_LENGTH)

    email_id = serializers.ReadOnlyField(
        source="email.subid")
    id = serializers.ReadOnlyField(
        source="subid")

    def validate_email(self, value: str) -> str | Email:
        # check already registered or not
        try:
            value = Email.objects.get(address=value)  # type: Email
        except ObjectDoesNotExist:
            pass
        else:
            if value.is_registered:
                self.fail("email_registered")
            if not value.allow_resend():
                self.fail("otp_already_sent")
        return value

    def create(self, validated_data: dict) -> Enrollment:
        request = self.context["request"]
        validated_data["device_id"] = request.COOKIES["device_id"]
        validated_data["user_agent"] = request.headers["User-Agent"]
        instance = Enrollment.objects.create(**validated_data)
        return instance
