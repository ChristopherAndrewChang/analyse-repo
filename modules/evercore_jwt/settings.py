from __future__ import annotations
from typing import TYPE_CHECKING

from evercore.settings import AppSetting

if TYPE_CHECKING:
    pass


__all__ = ("jwt_settings",)


DEFAULTS = {
    # registered claim keys
    # https://datatracker.ietf.org/doc/html/rfc7519#page-9
    "ISSUER_CLAIM": "iss",
    "SUBJECT_CLAIM": "sub",
    "AUDIENCE_CLAIM": "aud",
    "EXPIRATION_CLAIM": "exp",
    "NOT_BEFORE_CLAIM": "nbf",
    "ISSUED_AT_CLAIM": "iat",
    "TOKEN_ID_CLAIM": "jti",

    # evercore tech claim keys
    "TOKEN_TYPE_CLAIM": "tty",
}
jwt_settings = AppSetting(
    "EVERCORE_JWT_SETTINGS",
    DEFAULTS)
