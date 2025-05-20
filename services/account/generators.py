from __future__ import annotations
from typing import TYPE_CHECKING

from datetime import timedelta

from django.utils import timezone

from account.settings import account_settings

if TYPE_CHECKING:
    from datetime import datetime


__all__ = (
    "generate_otp_expires",
    "generate_otp_resend",
    "generate_otp_token_expires",
)


def generate_otp_expires(duration: int = None) -> datetime:
    if duration is None:
        duration = account_settings.DEFAULT_ENROLLMENT_PIN_DURATION
    return timezone.now() + timedelta(seconds=duration)


def generate_otp_resend(duration: int = None) -> datetime:
    if duration is None:
        duration = account_settings.DEFAULT_ENROLLMENT_PIN_RESEND
    return timezone.now() + timedelta(seconds=duration)


def generate_otp_token_expires(duration: int = None) -> datetime:
    if duration is None:
        duration = account_settings.DEFAULT_OTP_TOKEN_DURATION
    return timezone.now() + timedelta(seconds=duration)
