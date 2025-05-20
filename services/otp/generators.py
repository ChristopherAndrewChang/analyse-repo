from __future__ import annotations
from typing import TYPE_CHECKING

import logging
import random
import secrets
import string

from datetime import timedelta

from django.utils import timezone

from .settings import otp_settings

if TYPE_CHECKING:
    from datetime import datetime


logger = logging.getLogger(__name__)
__all__ = (
    "otp_number",
    "pin_number",
    "default_expires",
    "generate_token",
)


def otp_number(length: int = None) -> str:
    if length is None:
        length = otp_settings.DEFAULT_CODE_LENGTH
    return "".join(random.choices(string.digits, k=length))


def pin_number(length: int = None) -> str:
    if length is None:
        length = otp_settings.DEFAULT_PIN_LENGTH
    return "".join(random.choices(string.digits, k=length))


def default_expires(duration: int = None) -> datetime:
    if duration is None:
        duration = otp_settings.DEFAULT_PIN_DURATION
    return timezone.now() + timedelta(seconds=duration)


def generate_token(nbytes: int = None) -> str:
    if nbytes is None:
        nbytes = otp_settings.DEFAULT_OTP_TOKEN_BYTES_LENGTH
    return secrets.token_urlsafe(nbytes)
