from __future__ import annotations
from typing import TYPE_CHECKING

import base64
import binascii
import secrets

from datetime import timedelta

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

from django.utils import timezone

from authn.settings import authn_settings

if TYPE_CHECKING:
    import datetime


def generate_bytes(nbytes: int) -> bytes:
    return secrets.token_bytes(nbytes)


def generate_b64(nbytes: int) -> bytes:
    return base64.b64encode(secrets.token_bytes(nbytes))


def generate_urlsafe_b64(nbytes: int) -> bytes:
    return base64.urlsafe_b64encode(
        secrets.token_bytes(nbytes))


def generate_b32(nbytes: int) -> bytes:
    return base64.b32encode(secrets.token_bytes(nbytes))


def generate_hex(nbytes: int) -> bytes:
    return binascii.hexlify(secrets.token_bytes(nbytes))


def generate_rsa_private_key() -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend())


def generate_enrollment_otp_expires(duration: int = None) -> datetime.datetime:
    if duration is None:
        duration = authn_settings.ENROLLMENT_OTP_DURATION
    return timezone.now() + timedelta(seconds=duration)


def generate_enrollment_otp_resend(duration: int = None) -> datetime.datetime:
    if duration is None:
        duration = authn_settings.ENROLLMENT_OTP_RESEND
    return timezone.now() + timedelta(seconds=duration)


def generate_enrollment_token_expires(duration: int = None) -> datetime.datetime:
    if duration is None:
        duration = authn_settings.ENROLLMENT_TOKEN_DURATION
    return timezone.now() + timedelta(seconds=duration)
