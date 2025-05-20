from __future__ import annotations
from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _

from rest_framework.permissions import BasePermission

from rest_framework_simplejwt.exceptions import TokenError

if TYPE_CHECKING:
    from rest_framework.request import Request
    from evercore_jwt_auth.tokens import Token


__all__ = (
    "MultiFactorAuthRequired",
    "MultiFactorSessionAlive",
    "HasSelectedTenant",
)


class MultiFactorAuthRequired(BasePermission):
    message = _("Multi factor authentication required.")

    def has_permission(self, request: Request, view) -> bool:
        token = request.auth  # type: Token
        try:
            return token.multi_factor_auth
        except TokenError:
            return False


class MultiFactorSessionAlive(BasePermission):
    message = _("Multi factor session required.")

    def has_permission(self, request: Request, view) -> bool:
        token = request.auth  # type: Token
        return token.multi_factor_session_alive


class HasSelectedTenant(BasePermission):
    message = _("No tenant selected.")

    def has_permission(self, request: Request, view) -> bool:
        token = request.auth  # type: Token
        try:
            return bool(token.tenant_id)
        except TokenError:
            return False
