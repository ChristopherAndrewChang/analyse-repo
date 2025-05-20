from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from rest_framework import status
from rest_framework.exceptions import NotFound, Throttled
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from evercore_jwt_auth.rest_framework.authentication import JWTAuthentication
from evercore_jwt_auth.rest_framework.permissions import (
    MultiFactorSessionAlive,
)

from idvalid_core.rest.permissions import DeviceCookieRequired

from authn.models import BackupCode
from authn.models import CooldownError
from authn.rest.permissions import HasBackupCode

if TYPE_CHECKING:
    from rest_framework.request import Request
    from authn.models import User, UserMFA


logger = logging.getLogger(__name__)
__all__ = (
    "BackupCodeViewSet",
)


class BackupCodeViewSet(GenericViewSet):
    request: "Request"
    authentication_classes = (JWTAuthentication,)
    permission_classes = (
        DeviceCookieRequired,
        IsAuthenticated,
        MultiFactorSessionAlive,
    )

    def list(self, request: Request, *args, **kwargs):
        mfa = request.user.mfa  # type: UserMFA
        if not mfa.has_backup_code():
            raise NotFound()
        return Response(
            mfa.backup_code.available_codes, status=status.HTTP_200_OK)

    def update(self, request: Request, *args, **kwargs) -> Response:
        user = request.user  # type: User
        mfa = user.mfa  # type: UserMFA
        if mfa.has_backup_code():
            backup_code = mfa.backup_code
            try:
                backup_code.generate_challenge()
            except CooldownError:
                raise Throttled()
        else:
            backup_code = BackupCode.objects.create(
                created_by=user)
            mfa.set_backup_code(backup_code)
        return Response(
            backup_code.codes, status=status.HTTP_200_OK)
