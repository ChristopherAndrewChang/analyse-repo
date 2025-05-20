from __future__ import annotations
from typing import TYPE_CHECKING

from rest_framework.permissions import BasePermission, SAFE_METHODS

if TYPE_CHECKING:
    from rest_framework.request import Request
    from authn.models import User


__all__ = (
    "IsSafe",
    "HasAuthenticator",
    "HasSecurityCode",
)


class IsSafe(BasePermission):
    def has_permission(self, request: Request, view) -> bool:
        return request.method in SAFE_METHODS


class HasAuthenticator(BasePermission):
    def has_permission(self, request: Request, view) -> bool:
        user = request.user  # type: User
        return user.has_totp()


class HasSecurityCode(BasePermission):
    def has_permission(self, request: Request, view) -> bool:
        user = request.user  # type: User
        return user.has_security_code()
