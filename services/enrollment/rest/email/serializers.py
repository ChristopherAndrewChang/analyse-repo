from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

# from enrollment.locks import CacheLock
from enrollment.models import Enrollment, Otp, constants, Code, Email
from enrollment.settings import enrollment_settings

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "OTPSerializer",
    "CreateSerializer",
)


class OTPSerializer(serializers.ModelSerializer):
    default_error_messages = {
        "registered": _("Already registered."),
    }
    email = serializers.EmailField(
        source="enrollment", write_only=True)
    ref_id = serializers.ReadOnlyField(
        source="enrollment.subid")

    class Meta:
        model = Otp
        fields = (
            "id",
            "email",
            "state",
            "ref_id",
            "otp_id",
        )
        extra_kwargs = {
            "id": {
                "source": "subid",
                "read_only": True,
            },
            "state": {
                "min_length": constants.STATE_LENGTH,
                "write_only": True,
            },
            "otp_id": {"read_only": True},
        }
        read_only_fields = ("pk",)

    def validate_email(self, value: str) -> str | Enrollment:
        # check already registered or not
        try:
            value = Enrollment.objects.get(email=value)  # type: Enrollment
        except ObjectDoesNotExist:
            pass
        else:
            if value.is_registered:
                self.fail("registered")
        return value

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["device_id"] = request.COOKIES["device_id"]
        validated_data["user_agent"] = request.headers["User-Agent"]
        return super().create(validated_data)

        # from rest_framework.request import Request
        # from django.http import HttpRequest
        # request = self.context["request"]
        # raise Exception((
        #     request.COOKIES,
        #     request.headers,
        #     validated_data
        #     # self.context["request"].META
        # ))
        # raise Exception(self.context["request"].headers)
        # raise Exception(validated_data)


class CreateSerializer(serializers.Serializer):
    default_error_messages = {
        "email_registered": _("Already registered."),
        "otp_already_sent": _(
            f"OTP already sent to this email. Try again "
            f"in {enrollment_settings.OTP_DEFAULT_DURATION} seconds.")
    }

    email = serializers.EmailField(
        write_only=True)
    state = serializers.CharField(
        write_only=True,
        max_length=constants.STATE_LENGTH)

    ref_id = serializers.ReadOnlyField(
        source="email.subid")
    enrollment_id = serializers.ReadOnlyField(
        source="subid")

    def validate_email(self, value: str) -> str | Email:
        # check already registered or not
        try:
            value = Email.objects.get(email=value)  # type: Email
        except ObjectDoesNotExist:
            pass
        else:
            if value.is_registered:
                self.fail("email_registered")
            if not value.allow_resend():
                self.fail("otp_already_sent")
        return value

    def create(self, validated_data: dict) -> Code:
        request = self.context["request"]
        validated_data["device_id"] = request.COOKIES["device_id"]
        validated_data["user_agent"] = request.headers["User-Agent"]
        instance = Code.objects.create(**validated_data)
        return instance
