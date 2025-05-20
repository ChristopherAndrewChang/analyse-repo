from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from rest_framework import status
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from evercore_jwt_auth.rest_framework.authentication import JWTAuthentication
from evercore_jwt_auth.rest_framework.permissions import (
    MultiFactorSessionAlive,
)

from idvalid_core.rest.permissions import DeviceCookieRequired

from authn.models import TOTP

from authn.rest.permissions import (
    PlatformPermission,
)

from authn.rest.permissions import HasAuthenticator
from .serializers import (
    ConfirmSerializer,
)

if TYPE_CHECKING:
    from typing import Sequence
    from rest_framework.permissions import BasePermission
    from rest_framework.request import Request
    from authn.models import User, UserMFA


logger = logging.getLogger(__name__)
__all__ = (
    "AuthenticatorViewSet",
    # "ConfirmView",
)


class AuthenticatorViewSet(GenericViewSet):
    request: "Request"
    authentication_classes = (JWTAuthentication,)

    queryset = TOTP.objects.filter(
        confirmed=False,
        disabled=False
    )
    lookup_field = "subid"
    serializer_class = ConfirmSerializer

    def get_queryset(self):
        return super().get_queryset().filter(
            created_by=self.request.user)

    def get_permissions(self) -> Sequence[BasePermission]:
        action = self.action
        base_perms = (
            DeviceCookieRequired,
            PlatformPermission,
            IsAuthenticated,
            MultiFactorSessionAlive,
        )
        if action == "disable":
            self.permission_classes = base_perms + (
                HasAuthenticator,)
        else:
            self.permission_classes = base_perms
        return super().get_permissions()

    def generate(self, request: Request, *args, **kwargs) -> Response:
        user = request.user  # type: User
        instance = TOTP.objects.create(
            description="user",
            created_by=user
        )  # type: TOTP
        return Response({
            "pk": instance.subid,
            "url": instance.config_url(user.username)
        })

    def disable(self, request: Request, *args, **kwargs) -> Response:
        instance = request.user.mfa  # type: UserMFA
        instance.remove_totp()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def confirm(self, request: Request, *args, **kwargs):
        serializer = self.get_serializer(
            self.get_object(),
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
