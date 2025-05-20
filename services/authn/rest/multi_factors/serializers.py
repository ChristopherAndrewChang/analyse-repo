from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from webauthn.helpers.exceptions import WebAuthnException

from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, Throttled

from evercore.rest.fields import Base64Field

from authn.models import (
    # exceptions
    ThrottledError,
    NoPinError,

    # models
    Passkey,
)
from authn.rest.validators import DigitValidator
from authn.settings import authn_settings
from authn.tokens import AccessToken

if TYPE_CHECKING:
    from authn.models import User, EmailOTP, MobileOTP


logger = logging.getLogger(__name__)
__all__ = (
    "BaseVerifySerializer",
    "AuthenticatorSerializer",
    "EmailSerializer",
    "PasskeySerializer",
    "SecurityCodeSerializer",
    "BackupCodeSerializer",
    "CreateMobileSerializer",
    "MobileSerializer",
)


class BaseVerifySerializer(serializers.Serializer):
    instance: User

    def get_multi_factor_name(self) -> str:
        raise NotImplementedError

    def validate(self, attrs):
        token = self.context["request"].auth  # type: AccessToken
        refresh = token.get_refresh_token_instance()
        refresh.update_multi_factor(
            self.get_multi_factor_name(),
            current_time=token.current_time
        )
        return {
            "access_token": str(
                refresh.get_access_jwt(current_time=token.current_time)
            ),
        }


class EmailSerializer(BaseVerifySerializer):
    default_error_messages = {
        "invalid_pin": _("Invalid pin.")
    }

    pin = serializers.CharField(
        min_length=authn_settings.EMAIL_OTP_PIN_LENGTH,
        max_length=authn_settings.EMAIL_OTP_PIN_LENGTH,
        validators=[DigitValidator()])

    def validate_pin(self, value: str):
        instance = self.instance.emailotp_set.get()  # type: EmailOTP
        try:
            verified = instance.verify(value)
        except NoPinError:
            raise PermissionDenied()
        except ThrottledError:
            raise Throttled()
        else:
            if not verified:
                self.fail("invalid_pin")

    def get_multi_factor_name(self) -> str:
        return "email"


class CreateMobileSerializer(serializers.Serializer):
    state = Base64Field(
        max_length=32,
        min_length=32,
        strict=False,
        write_only=True)
    id = serializers.ReadOnlyField(
        source="subid")
    challenge = serializers.ReadOnlyField(
        source="_pin")
    valid_until = serializers.DateTimeField(
        # source="valid_until",
        read_only=True
    )

    def create(self, validated_data: dict) -> MobileOTP:
        user = self.context["request"].user
        return user.mobileotp_set.create(
            **validated_data)


class MobileSerializer(BaseVerifySerializer):
    instance: MobileOTP

    default_error_messages = {
        "invalid_state": _("Invalid.")
    }

    state = serializers.CharField()

    def validate_state(self, value: str) -> None:
        if not self.instance.check_state(value):
            self.fail("invalid_state")
        return None

    def validate(self, attrs: dict) -> dict | None:
        instance = self.instance
        if not instance.accepted:
            attrs = {}
        else:
            attrs = super().validate(attrs)
        instance.delete()
        return attrs

    def get_multi_factor_name(self) -> str:
        return "mobile"


class AuthenticatorSerializer(BaseVerifySerializer):
    default_error_messages = {
        "invalid_pin": _("Invalid pin.")
    }

    pin = serializers.CharField(
        min_length=4, max_length=9,
        validators=[DigitValidator()])

    def validate_pin(self, value: str):
        if not self.instance.mfa.totp.verify(value):
            self.fail("invalid_pin")

    def get_multi_factor_name(self) -> str:
        return "authenticator"


class SecurityCodeSerializer(BaseVerifySerializer):
    default_error_messages = {
        "invalid_pin": _("Invalid pin.")
    }

    pin = serializers.CharField(
        validators=[DigitValidator()])

    def validate_pin(self, value: str):
        if not self.instance.mfa.security_code.verify(value):
            self.fail("invalid_pin")

    def get_multi_factor_name(self) -> str:
        return "security-code"


class BackupCodeSerializer(BaseVerifySerializer):
    default_error_messages = {
        "invalid_pin": _("Invalid pin.")
    }

    pin = serializers.CharField()

    def validate_pin(self, value: str):
        try:
            if not self.instance.mfa.backup_code.verify(value):
                self.fail("invalid_pin")
        except ThrottledError:
            raise Throttled()

    def get_multi_factor_name(self) -> str:
        return "backup-code"


class PasskeySerializer(BaseVerifySerializer):
    default_error_messages = {
        "invalid_cred": _("Invalid Credential."),
        "invalid_cred_id": _("Invalid Credential ID.")
    }

    cred = serializers.DictField(allow_empty=False)

    def validate_cred(self, value: dict) -> Passkey:
        try:
            return self.instance.verify(value)
        except WebAuthnException as e:
            raise serializers.ValidationError(
                str(e), code="invalid_cred")

    def get_multi_factor_name(self) -> str:
        return "passkey"
