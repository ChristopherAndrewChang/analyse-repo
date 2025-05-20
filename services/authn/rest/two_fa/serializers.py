from __future__ import annotations
from typing import TYPE_CHECKING

import logging
# import struct

from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

# from evercore.rest import Base64Field
from authn.models import SecurityCode
from authn.rest.validators import DigitValidator
from authn.settings import authn_settings
from authn.tokens import RefreshToken

if TYPE_CHECKING:
    from authn.models import TOTP, User


logger = logging.getLogger(__name__)
__all__ = (
    "ConfirmAuthenticatorSerializer",
    "VerifyAuthenticatorSerializer",

    "SetSecurityCodeSerializer",
    "ChangeSecurityCodeSerializer",
    "VerifySecurityCodeSerializer",
)


class ConfirmAuthenticatorSerializer(serializers.Serializer):
    default_error_messages = {
        "invalid_format": _("Invalid format."),
        "incorrect": _("Incorrect.")
    }

    code = serializers.CharField(
        min_length=4, max_length=9,
        validators=[DigitValidator()])

    def validate_code(self, value: str) -> str:
        instance = self.instance  # type: TOTP
        if not instance.verify(value):
            self.fail("incorrect")
        return value

    def update(self, instance: TOTP, validated_data: dict) -> TOTP:
        request = self.context["request"]
        user = request.user  # type: User
        user.set_totp(instance)
        return instance


class VerifyAuthenticatorSerializer(serializers.Serializer):
    instance: User
    token_class = RefreshToken
    default_error_messages = {
        "invalid_pin": _("Invalid pin.")
    }

    pin = serializers.CharField(
        min_length=4, max_length=9,
        validators=[DigitValidator()])

    def validate_pin(self, value: str):
        if not self.instance.totp.verify(value):
            self.fail("invalid_pin")

    def validate(self, attrs) -> dict:
        refresh = self.token_class.for_user(self.instance)
        refresh.set_2fa_exp()
        return {
            "refresh_token": str(refresh),
            "access_token": str(refresh.access_token),
        }


class SetSecurityCodeSerializer(serializers.Serializer):
    new_pin = serializers.CharField(
        source="pin",
        max_length=authn_settings.SECURITY_CODE_PIN_LENGTH,
        min_length=authn_settings.SECURITY_CODE_PIN_LENGTH,
        validators=[DigitValidator()]
    )

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user  # type: User
        instance = SecurityCode.objects.create(
            created_by=user,
            **validated_data)
        user.set_security_code(instance)
        return instance


class ChangeSecurityCodeSerializer(SetSecurityCodeSerializer):
    default_error_messages = {
        "invalid_old_pin": _("Invalid.")
    }
    old_pin = serializers.CharField()

    def validate_old_pin(self, value: str) -> str:
        user = self.context["request"].user  # type: User
        if not user.security_code.verify(value):
            self.fail("invalid_old_pin")
        return value

    def validate(self, attrs):
        attrs.pop("old_pin")
        return attrs


class VerifySecurityCodeSerializer(serializers.Serializer):
    instance: User
    token_class = RefreshToken
    default_error_messages = {
        "invalid_pin": _("Invalid pin.")
    }

    pin = serializers.CharField(
        validators=[DigitValidator()])

    def validate_pin(self, value: str):
        if not self.instance.security_code.verify(value):
            self.fail("invalid_pin")

    def validate(self, attrs) -> dict:
        refresh = self.token_class.for_user(self.instance)
        refresh.set_2fa_exp()
        return {
            "refresh_token": str(refresh),
            "access_token": str(refresh.access_token),
        }
