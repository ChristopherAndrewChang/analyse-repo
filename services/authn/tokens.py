from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from evercore_jwt_auth import tokens
from evercore_jwt_auth.settings import jwt_auth_settings

from authn.models import (
    RefreshToken as RefreshTokenModel,
    Session,
)

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "Token",
    "AccessToken",
    "RefreshToken",
)


class Token(tokens.Token):
    def get_session_instance(self) -> Session | None:
        try:
            return Session.objects.get(
                pk=self.session_id,
                user_id=self.subject)
        except Session.DoesNotExist:
            return None

    def get_refresh_token_instance(self) -> RefreshTokenModel | None:
        try:
            return RefreshTokenModel.objects.get(
                pk=self.refresh_token_id)
        except RefreshTokenModel.DoesNotExist:
            return None


class AccessToken(Token):
    token_type = "access"
    lifetime = jwt_auth_settings.ACCESS_TOKEN_LIFETIME


class RefreshToken(Token):
    token_type = "refresh"
    lifetime = jwt_auth_settings.REFRESH_TOKEN_LIFETIME
