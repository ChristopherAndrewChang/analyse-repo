from __future__ import annotations
from typing import TYPE_CHECKING

from evercore.settings import AppSetting

if TYPE_CHECKING:
    pass


__all__ = ("enrollment_settings",)


DEFAULTS = {
    "OTP_DEFAULT_RESEND": 3 * 60,  # 3 minutes
    "OTP_DEFAULT_DURATION": 60 * 10,  # 10 minutes (600 seconds)
}

MANDATORY = ("OTP_DEFAULT_RESEND", "OTP_DEFAULT_DURATION")


enrollment_settings = AppSetting(
    "IDVALID_ENROLLMENT_SETTINGS",
    DEFAULTS,
    mandatory=MANDATORY)
