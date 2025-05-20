from __future__ import annotations
from typing import TYPE_CHECKING

from evercore.settings import AppSetting

if TYPE_CHECKING:
    pass


__all__ = ("otp_settings",)


DEFAULTS = {
    "DEFAULT_CODE_LENGTH": 6,
    "DEFAULT_PIN_LENGTH": 8,
    "DEFAULT_PIN_DURATION": 60 * 60,  # 1 hour (3600 seconds)
    "DEFAULT_OTP_TOKEN_BYTES_LENGTH": 48,  # 64 in base64

    "TWILIO_API_KEY": "",
    "TWILIO_API_SECRET": "",
    "TWILIO_ACCOUNT_SID": "",
    "TWILIO_VERIFY_SID": "",
}


MANDATORY = (
    "DEFAULT_CODE_LENGTH",
    "DEFAULT_PIN_LENGTH",
    "DEFAULT_PIN_DURATION",
    "DEFAULT_OTP_TOKEN_BYTES_LENGTH",
)


otp_settings = AppSetting(
    "IDVALID_OTP_SETTINGS",
    DEFAULTS,
    mandatory=MANDATORY)
