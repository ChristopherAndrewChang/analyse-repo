from __future__ import annotations
from typing import TYPE_CHECKING

import logging
import struct

from webauthn.helpers.exceptions import WebAuthnException

from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from phonenumber_field.serializerfields import PhoneNumberField

# from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework_simplejwt.settings import (
#     api_settings as simplejwt_settings,
# )

from evercore.rest import Base64Field

from authn.models import (
    User,
    RefreshToken as RefreshTokenModel
)
# from authn.tokens import RefreshToken

if TYPE_CHECKING:
    # from typing import Any

    from authn.models import Passkey


logger = logging.getLogger(__name__)
__all__ = (
    "PasskeyLoginSerializer",
    "LoginSerializer",
    "EmailLoginSerializer",
    "PhoneLoginSerializer",
    "TokenRefreshSerializer",
)


class BaseLoginSerializer(serializers.Serializer):
    default_error_messages = {
        "invalid_credential": _("Cannot login with provided credential."),
        "no_active_account": _("No active account found with the given credentials."),
    }

    @property
    def mfa_required(self) -> bool:
        raise NotImplementedError

    @property
    def mfa_ref(self) -> str | None:
        return None

    def validate(self, attrs: dict) -> dict:
        request = self.context["request"]
        user = attrs["user"]  # type: User | None

        # No need to check `is_active` flag.
        # It's already checks in authenticate function

        if not user or not user.is_active:
            raise AuthenticationFailed(
                self.error_messages["no_active_account"],
                code="no_active_account")
        # populate mfa_required before calling user.login function
        mfa_required = (
            False
            if user.log.last_login is None else
            self.mfa_required
        )
        session = user.login(request)
        refresh = session.generate_refresh_token(
            mfa_required=mfa_required, mfa_ref=self.mfa_ref)
        return {
            "refresh_token": str(refresh.get_refresh_jwt()),
            "access_token": str(refresh.get_access_jwt()),
            "refresh_id": refresh.subid
        }


class PasskeyLoginSerializer(BaseLoginSerializer):
    default_error_messages = {
        "invalid_credential": _("Cannot login with provided credential."),
    }
    mfa_required = False
    mfa_ref = "passkey"

    cred = serializers.DictField(allow_empty=False)

    def validate_cred(self, value: dict) -> Passkey:
        try:
            return self.instance.verify(value)
        except WebAuthnException as e:
            raise serializers.ValidationError(
                str(e), code="invalid_credential")

    def validate(self, attrs: dict) -> dict:
        attrs["user"] = attrs.pop("cred").user
        return super().validate(attrs)


class BasePasswordLoginSerializer(BaseLoginSerializer):
    default_error_messages = {
        "invalid_credential": _("Cannot login with provided credential."),
    }
    mfa_required = True
    # token_class = RefreshToken

    password = Base64Field(strict=False, urlsafe=True)

    def _validate_password(self, value: bytes) -> bytes:
        request = self.context["request"]
        try:
            return request.platform.decrypt(
                value, struct.pack(b'>Q', request.timestamp))
        except ValueError:
            self.fail("invalid_credential")

    def authenticate_user(self, password: bytes, attrs: dict) -> User | None:
        raise NotImplementedError

    def validate(self, attrs: dict) -> dict:
        password = self._validate_password(attrs.pop("password"))
        attrs["user"] = self.authenticate_user(password, attrs)
        return super().validate(attrs)


class LoginSerializer(BasePasswordLoginSerializer):
    username = serializers.CharField(
        validators=[User.username_validator])

    def authenticate_user(self, password: bytes, attrs: dict) -> User | None:
        return authenticate(
            self.context["request"],
            field="username",
            password=password,
            **attrs)


class EmailLoginSerializer(BasePasswordLoginSerializer):
    email = serializers.EmailField()

    def authenticate_user(self, password: bytes, attrs: dict) -> User | None:
        return authenticate(
            self.context["request"],
            field="email",
            password=password,
            **attrs)


class PhoneLoginSerializer(BasePasswordLoginSerializer):
    phone = PhoneNumberField()

    def authenticate_user(self, password: bytes, attrs: dict) -> User | None:
        return authenticate(
            self.context["request"],
            field="phone",
            password=password,
            **attrs)


class TokenRefreshSerializer(serializers.Serializer):
    default_error_messages = {
        "refresh_invalid": _("Cannot refresh with provided credential."),
        "refresh_expired": _("Expired.")
    }
    # refresh_token = serializers.CharField()
    access_token = serializers.CharField(read_only=True)
    refresh = Base64Field(
        strict=False, urlsafe=True)
    # token_class = RefreshToken

    def validate_refresh(self, value: bytes) -> RefreshTokenModel:
        # raise Exception(value)
        request = self.context["request"]
        try:
            value = request.platform.decrypt(
                value, struct.pack(b'>Q', request.timestamp))
        except ValueError:
            self.fail("refresh_invalid")

        try:
            refresh = RefreshTokenModel.objects.get(
                subid=value.decode())  # type: RefreshTokenModel
        except ObjectDoesNotExist:
            self.fail("refresh_invalid")

        # noinspection PyUnboundLocalVariable
        if request.auth.refresh_token_id != refresh.id:
            self.fail("refresh_invalid")

        if not refresh.is_alive:
            self.fail("refresh_expired")

        return refresh

    def validate(self, attrs):
        return {
            "access_token": str(attrs["refresh"].get_access_jwt()),
        }
        # raise Exception(attrs)

    # def validate(self, attrs: "dict[str, Any]") -> "dict[str, str]":
    #     refresh = self.token_class(attrs["refresh_token"])
    #
    #     data = {"access_token": str(refresh.access_token)}
    #
    #     if simplejwt_settings.ROTATE_REFRESH_TOKENS:
    #         if simplejwt_settings.BLACKLIST_AFTER_ROTATION:
    #             try:
    #                 # Attempt to blacklist the given refresh token
    #                 refresh.blacklist()
    #             except AttributeError:
    #                 # If blacklist app not installed, `blacklist` method will
    #                 # not be present
    #                 pass
    #
    #         refresh.set_jti()
    #         refresh.set_exp()
    #         refresh.set_iat()
    #
    #         data["refresh_token"] = str(refresh)
    #
    #     return data
