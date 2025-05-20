from __future__ import annotations
from typing import TYPE_CHECKING

from evercore.settings import AppSetting

if TYPE_CHECKING:
    pass


__all__ = ("account_settings",)


DEFAULTS = {
    "DEFAULT_ENROLLMENT_PIN_RESEND": 5 * 60,  # 5 minutes
    "DEFAULT_ENROLLMENT_PIN_DURATION": 10 * 60,  # 10 minutes (600 seconds)
    "DEFAULT_OTP_TOKEN_DURATION": 2 * 60 * 60,  # 2 hours
}

MANDATORY = (
    "DEFAULT_ENROLLMENT_PIN_RESEND",
    "DEFAULT_ENROLLMENT_PIN_DURATION",
    "DEFAULT_OTP_TOKEN_DURATION",
)


account_settings = AppSetting(
    "IDVALID_ACCOUNT_SETTINGS",
    DEFAULTS,
    mandatory=MANDATORY)
