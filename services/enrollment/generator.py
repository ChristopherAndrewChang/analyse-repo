from __future__ import annotations
from typing import TYPE_CHECKING

from datetime import timedelta

from django.utils import timezone

from enrollment.settings import enrollment_settings

if TYPE_CHECKING:
    from datetime import datetime


__all__ = (
    "generate_otp_expires",
    "generate_otp_resend"
)


def generate_otp_expires(duration: int = None) -> datetime:
    if duration is None:
        duration = enrollment_settings.OTP_DEFAULT_DURATION
    return timezone.now() + timedelta(seconds=duration)


def generate_otp_resend(duration: int = None) -> datetime:
    if duration is None:
        duration = enrollment_settings.OTP_DEFAULT_RESEND
    return timezone.now() + timedelta(seconds=duration)
