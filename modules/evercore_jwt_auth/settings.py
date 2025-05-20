from __future__ import annotations
from typing import TYPE_CHECKING

from datetime import timedelta

from django.conf import settings

from evercore.settings import AppSetting

if TYPE_CHECKING:
    pass


__all__ = ("jwt_auth_settings",)


DEFAULTS = {
    # ##### #
    # Authn #
    # ##### #
    "AUTHN_MULTI_FACTOR_AUTH_CLAIM": "mfa",
    "AUTHN_MULTI_FACTOR_EXPIRATION_CLAIM": "mfe",
    "AUTHN_MULTI_FACTOR_REFERENCE_CLAIM": "mfr",
    "AUTHN_MULTI_FACTOR_SESSION_LIFETIME": timedelta(minutes=5),
    "AUTHN_SESSION_ID_CLAIM": "sid",
    "AUTHN_REFRESH_TOKEN_ID_CLAIM": "rti",
    "AUTHN_PLATFORM_TYPE_CLAIM": "pft",

    # ###### #
    # Tenant #
    # ###### #
    # tenant claim settings
    "TENANT_ID_CLAIM": "tni",
    "TENANT_OWNER_CLAIM": "tno",

    # #### #
    # RBAC #
    # #### #
    # rbac claim settings
    "RBAC_ROLE_IDS_CLAIM": "rri",

    # backend settings
    "ALGORITHM": "HS256",
    "SIGNING_KEY": settings.SECRET_KEY,
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "JSON_ENCODER": None,

    # token settings
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "ACCESS_TOKEN_CLASS": "evercore_jwt_auth.tokens.AccessToken",
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_CLASS": "evercore_jwt_auth.tokens.RefreshToken",

    # authentication settings
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "AUTH_TOKEN_CLASSES": (
        "evercore_jwt_auth.tokens.AccessToken",
        # "evercore_jwt_auth.tokens.RefreshToken",
    ),
    "USER_ID_CLAIM": "sub",
    "USER_ID_FIELD": "id",
    "TOKEN_USER_CLASS": "evercore_jwt_auth.models.TokenUser",
}

MANDATORY = (
    "ACCESS_TOKEN_CLASS",
    "REFRESH_TOKEN_CLASS",
)

IMPORT_STRINGS = (
    "JSON_ENCODER",
    "ACCESS_TOKEN_CLASS",
    "REFRESH_TOKEN_CLASS",
    "AUTH_TOKEN_CLASSES",
    "TOKEN_USER_CLASS",
)

jwt_auth_settings = AppSetting(
    "EVERCORE_JWT_AUTH_SETTINGS",
    DEFAULTS,
    mandatory=MANDATORY,
    import_strings=IMPORT_STRINGS)
