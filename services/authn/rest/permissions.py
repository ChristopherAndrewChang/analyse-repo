from __future__ import annotations
from typing import TYPE_CHECKING

import binascii
import time

from django.utils.translation import gettext_lazy as _

from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

from rest_framework_simplejwt.exceptions import TokenError

from authn.models import Platform
from authn.settings import authn_settings
from authn.utils import b64decode, login_key

if TYPE_CHECKING:
    from rest_framework.request import Request
    from authn.models import Enrollment, ForgetPassword, User


__all__ = (
    "PlatformPermission",
    "OtpTokenPermission",
    "LoginTwoFARequired",
    "TwoFARequired",

    "HasEmail",
    "HasPhone",
    "HasAuthenticator",
    "HasBackupCode",
    "HasPasskey",
    "HasSecurityCode",
    "HasMobileLoggedIn",
)


MISSING_HEADER_MESSAGE = _("Missing header {}.")
INVALID_HEADER_MESSAGE = _("Invalid header {}.")


def _get_params(request: Request, key: str) -> bytes:
    try:
        value = request.headers[key]
    except KeyError:
        raise PermissionDenied(MISSING_HEADER_MESSAGE.format(key))
    if value == '':
        raise PermissionDenied(MISSING_HEADER_MESSAGE.format(key))
    try:
        return b64decode(value, urlsafe=True)
    except binascii.Error:
        raise PermissionDenied(INVALID_HEADER_MESSAGE.format(key))


class PlatformPermission(BasePermission):
    platform_label_header = authn_settings.SECURITY_PLATFORM_LABEL_HEADER
    platform_id_header = authn_settings.SECURITY_PLATFORM_ID_HEADER
    timestamp_header = authn_settings.SECURITY_TIMESTAMP_HEADER
    nonce_header = authn_settings.SECURITY_NONCE_HEADER

    default_error_messages = {
        # "missing": _("Missing credential."),
        "invalid": _("Invalid credential."),
        "too_old": _("Request too old."),
    }

    def fail(self, key: str):
        message = self.default_error_messages[key]
        raise PermissionDenied(detail=message, code=key)

    def decrypt_platform_id(self, request: Request) -> bytes:
        try:
            return login_key.decrypt(
                _get_params(request, self.platform_id_header),
                _get_params(request, self.platform_label_header))
        except ValueError:
            self.fail("invalid")

    def get_platform(self, request: Request) -> Platform:
        try:
            return Platform.objects.select_related(
                "totp_device"
            ).get(subid=self.decrypt_platform_id(request).decode())
        except Platform.DoesNotExist:
            self.fail("invalid")

    def get_timestamp(self, request: Request) -> int:
        timestamp_int = int.from_bytes(
            _get_params(request, self.timestamp_header), byteorder="big")
        drift = int(time.time()) - timestamp_int
        if abs(drift) > authn_settings.SECURITY_MAX_TIMESTAMP_DRIFT:
            self.fail("too_old")
        return timestamp_int

    def get_nonce(self, request: Request) -> bytes:
        return _get_params(request, self.nonce_header)

    def has_permission(self, request: Request, view) -> bool:
        platform = self.get_platform(request)
        timestamp = self.get_timestamp(request)
        if not platform.totp_device.verify_bytes(
                self.get_nonce(request),
                at=timestamp,
                tolerance=0):
            self.fail("invalid")
        request.platform = platform
        request.timestamp = timestamp
        return True


class OtpTokenPermission(BasePermission):
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
            self, request: Request, view,
            obj: Enrollment | ForgetPassword) -> bool:
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


class LoginTwoFARequired(BasePermission):
    message = _("Login two factor authentication required.")

    def has_permission(self, request: Request, view) -> bool:
        try:
            return request.auth.is_2fa_passed()
        except TokenError:
            return False


class TwoFARequired(BasePermission):
    message = _("Two factor authentication required.")

    def has_permission(self, request: Request, view) -> bool:
        try:
            request.auth.check_2fa_exp()
        except TokenError:
            return False
        return True


class HasEmail(BasePermission):
    def has_permission(self, request: Request, view) -> bool:
        user = request.user  # type: User
        return user.has_email()


class HasPhone(BasePermission):
    def has_permission(self, request: Request, view) -> bool:
        user = request.user  # type: User
        return user.has_phone()


class HasAuthenticator(BasePermission):
    def has_permission(self, request: Request, view) -> bool:
        return request.user.mfa.has_totp()


class HasBackupCode(BasePermission):
    def has_permission(self, request: Request, view) -> bool:
        return request.user.mfa.has_backup_code()


class HasPasskey(BasePermission):
    def has_permission(self, request: Request, view) -> bool:
        return request.user.mfa.has_passkey()


class HasSecurityCode(BasePermission):
    def has_permission(self, request: Request, view) -> bool:
        return request.user.mfa.has_security_code()


class HasMobileLoggedIn(BasePermission):
    def has_permission(self, request: Request, view) -> bool:
        return request.user.mfa.has_mobile_logged_in()
