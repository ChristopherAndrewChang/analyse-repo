from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from phonenumber_field.serializerfields import PhoneNumberField

from authn.models import constants, Enrollment, Email, Phone
from authn.settings import authn_settings

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "EmailSerializer",
    "PhoneSerializer",
)


class BaseCreateSerializer(serializers.Serializer):
    state = serializers.CharField(
        write_only=True,
        max_length=constants.ENROLLMENT_STATE_LENGTH)

    id = serializers.ReadOnlyField(
        source="subid")

    def create_object(self, validated_data: dict) -> Enrollment:
        raise NotImplementedError

    def create(self, validated_data: dict) -> Enrollment:
        request = self.context["request"]
        validated_data["device_id"] = request.COOKIES["device_id"]
        validated_data["user_agent"] = request.headers["User-Agent"]
        return self.create_object(validated_data)


class EmailSerializer(BaseCreateSerializer):
    default_error_messages = {
        "registered": _("Already registered."),
        "otp_already_sent": _(
            f"OTP already sent to this email. Try again "
            f"in {authn_settings.ENROLLMENT_OTP_RESEND} seconds.")
    }

    email = serializers.EmailField(
        write_only=True)

    email_id = serializers.ReadOnlyField(
        source="email.subid")

    def validate_email(self, value: str) -> str | Email:
        # check already registered or not
        try:
            value = Email.objects.get(address=value)  # type: Email
        except ObjectDoesNotExist:
            pass
        else:
            if value.is_registered:
                self.fail("registered")
            if not value.allow_resend():
                self.fail("otp_already_sent")
        return value

    def create_object(self, validated_data: dict) -> Enrollment:
        return Enrollment.objects.create_email(**validated_data)


class PhoneSerializer(BaseCreateSerializer):
    default_error_messages = {
        "registered": _("Already registered."),
        "otp_already_sent": _(
            f"OTP already sent to this number. Try again "
            f"in {authn_settings.ENROLLMENT_OTP_RESEND} seconds.")
    }

    phone = PhoneNumberField(
        write_only=True)

    phone_id = serializers.ReadOnlyField(
        source="phone.subid")

    def validate_phone(self, value: str) -> str | Phone:
        # check already registered or not
        try:
            value = Phone.objects.get(number=value)  # type: Email
        except ObjectDoesNotExist:
            pass
        else:
            if value.is_registered:
                self.fail("email_registered")
            if not value.allow_resend():
                self.fail("otp_already_sent")
        return value

    def create_object(self, validated_data: dict) -> Enrollment:
        return Enrollment.objects.create_phone(**validated_data)
