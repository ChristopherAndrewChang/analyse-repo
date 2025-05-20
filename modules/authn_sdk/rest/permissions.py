from __future__ import annotations
from typing import TYPE_CHECKING

from rest_framework.permissions import BasePermission

if TYPE_CHECKING:
    from rest_framework.request import Request
    from evercore_jwt_auth.tokens import AccessToken


__all__ = (
    "MobileAccessPermission",
    "NonMobileAccessPermission",
)


class MobileAccessPermission(BasePermission):
    def has_permission(self, request: Request, view):
        token = request.auth  # type: AccessToken
        return token.is_mobile


class NonMobileAccessPermission(BasePermission):
    def has_permission(self, request: Request, view):
        token = request.auth  # type: AccessToken
        return not token.is_mobile
