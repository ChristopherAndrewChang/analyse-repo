from __future__ import annotations
from typing import TYPE_CHECKING

from evercore.settings import AppSetting

if TYPE_CHECKING:
    pass


__all__ = ("authn_settings",)


DEFAULTS = {
    "DEFAULT_USER_LOOKUP_FIELD": "username",

    "PLATFORM_PRIVATE_KEY_SECRET": None,
    "LOGIN_PRIVATE_KEY_PEM": "test_rsa_private_key.pem",
    "LOGIN_PRIVATE_KEY_PASSPHRASE": None,
    "LOGIN_MAX_TIMESTAMP_DRIFT": 5,  # 5 seconds

    "ENROLLMENT_OTP_RESEND": 5 * 60,  # 5 minutes
    "ENROLLMENT_OTP_DURATION": 10 * 60,  # 10 minutes
    "ENROLLMENT_TOKEN_DURATION": 2 * 60 * 60,  # 2 hours

    "FORGET_PASSWORD_OTP_RESEND": 5 * 60,  # 5 minutes
    "FORGET_PASSWORD_OTP_DURATION": 10 * 60,  # 10 minutes

    "CHANGE_EMAIL_OTP_DURATION": 5 * 60,  # 5 minutes

    "SECURITY_PLATFORM_LABEL_HEADER": "X-Idv-Slt",
    "SECURITY_PLATFORM_ID_HEADER": "X-Idv-Pf",
    "SECURITY_TIMESTAMP_HEADER": "X-Idv-Ts",
    "SECURITY_NONCE_HEADER": "X-Idv-Nc",
    "SECURITY_2FA_HEADER": "X-Idv-Tfa",
    "SECURITY_MAX_TIMESTAMP_DRIFT": 10,  # 10 seconds

    "TOTP_DEFAULT_ISSUER": "IDValid",
    "TOTP_THROTTLE_FACTOR": 1,

    "PIN_THROTTLE_FACTOR": 1,

    "SECURITY_CODE_THROTTLE_FACTOR": 1,
    "SECURITY_CODE_PIN_LENGTH": 6,

    "EMAIL_OTP_PIN_LENGTH": 6,
    "EMAIL_OTP_PIN_DURATION": 5 * 60,  # 5 minutes
    "EMAIL_OTP_COOLDOWN_DURATION": 60,  # 60 seconds
    "EMAIL_OTP_THROTTLE_FACTOR": 1,

    "MOBILE_OTP_PIN_LENGTH": 2,
    "MOBILE_OTP_PIN_DURATION": 2 * 60,  # 1 minute

    "BACKUP_CODES_LENGTH": 10,
    "BACKUP_CODES_ITEM_BYTES_LENGTH": 5,  # 5 bytes length per item (10 hex chars)
    "BACKUP_CODES_COOLDOWN_DURATION": 60,  # 60 seconds
    "BACKUP_CODES_THROTTLE_FACTOR": 1,

    "PASSKEY_RP_ID": "idval.id",
    "PASSKEY_RP_NAME": "IDValid",
    "PASSKEY_DEFAULT_TIMEOUT": 60 * 1000,  # 60 seconds (60,000 milliseconds)
    "PASSKEY_ALLOWED_ORIGIN": [],
    "PASSKEY_SUPPORTED_ALGORITHMS": (
        # https://www.iana.org/assignments/cose/cose.xhtml#algorithms
        -7,    # ECDSA_SHA_256,
        -8,    # EDDSA,
        -36,   # ECDSA_SHA_512,
        -37,   # RSASSA_PSS_SHA_256,
        -38,   # RSASSA_PSS_SHA_384,
        -39,   # RSASSA_PSS_SHA_512,
        -257,  # RSASSA_PKCS1_v1_5_SHA_256,
        -258,  # RSASSA_PKCS1_v1_5_SHA_384,
        -259,  # RSASSA_PKCS1_v1_5_SHA_512,
    ),
}

MANDATORY = (
    "DEFAULT_USER_LOOKUP_FIELD",

    "ENROLLMENT_OTP_RESEND",
    "ENROLLMENT_OTP_DURATION",
    "ENROLLMENT_TOKEN_DURATION",

    "FORGET_PASSWORD_OTP_RESEND",
    "FORGET_PASSWORD_OTP_DURATION",

    "SECURITY_PLATFORM_LABEL_HEADER",
    "SECURITY_PLATFORM_ID_HEADER",
    "SECURITY_TIMESTAMP_HEADER",
    "SECURITY_NONCE_HEADER",
    "SECURITY_2FA_HEADER",

    "TOTP_THROTTLE_FACTOR",
    "PIN_THROTTLE_FACTOR",
)


authn_settings = AppSetting(
    "IDVALID_AUTH_SETTINGS",
    DEFAULTS,
    mandatory=MANDATORY)
