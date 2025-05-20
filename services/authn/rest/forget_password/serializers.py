from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from django.utils.crypto import constant_time_compare

from rest_framework import serializers

from authn.models import constants, User, ForgetPassword, ForgetPasswordState
from authn.settings import authn_settings

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "CreateSerializer",
    "ResetPasswordSerializer"
)


class CreateSerializer(serializers.Serializer):
    default_error_messages = {
        "email_not_registered": _("Not registered."),
        "otp_already_sent": _(
            f"OTP already sent to this email. Try again "
            f"in {authn_settings.FORGET_PASSWORD_OTP_RESEND} seconds.")
    }

    email = serializers.EmailField(
        source="user",
        write_only=True)
    state = serializers.CharField(
        write_only=True,
        max_length=constants.FORGET_PASSWORD_STATE_LENGTH)

    ref_id = serializers.ReadOnlyField(
        source="user.subid")
    id = serializers.ReadOnlyField(
        source="subid")

    def validate_email(self, value: str) -> User:
        try:
            instance = User.objects.get(
                email=value.lower()
            )  # type: User
        except ObjectDoesNotExist:
            self.fail("email_not_registered")
        else:
            try:
                state = instance.fp_state
            except ObjectDoesNotExist:
                pass
            else:
                if not state.allow_resend():
                    self.fail("otp_already_sent")
            return instance

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["device_id"] = request.COOKIES["device_id"]
        validated_data["user_agent"] = request.headers["User-Agent"]
        instance = ForgetPassword.objects.create(**validated_data)
        user = validated_data["user"]  # type: User
        try:
            state = user.fp_state
        except ObjectDoesNotExist:
            ForgetPasswordState.objects.create(
                user=user)
        else:
            state.renew_resend_date()
        return instance


class ResetPasswordSerializer(serializers.Serializer):
    instance: "ForgetPassword"
    default_error_messages = {
        "invalid_param": _("Invalid."),
    }

    state = serializers.CharField()
    otp_id = serializers.CharField()
    otp_token = serializers.CharField()

    password = serializers.CharField(
        validators=[validate_password])

    def validate_state(self, value: str):
        instance = self.instance
        if not instance.check_state(value):
            self.fail("invalid_param")
        return None

    def validate_otp_id(self, value: str):
        instance = self.instance
        if not constant_time_compare(
                instance.otp_token.subid, value):
            self.fail("invalid_param")

    def validate_otp_token(self, value: str):
        instance = self.instance
        if not constant_time_compare(
                instance.otp_token.token, value):
            self.fail("invalid_param")

    def update(self, instance: ForgetPassword, validated_data: dict) -> User:
        # raise Exception(instance, validated_data)
        user = instance.user
        user.update_password(validated_data["password"])
        instance.otp_token.apply()
        user.fp_state.clear_resend_date()
        return instance
