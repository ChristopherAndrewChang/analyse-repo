from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from rest_framework import status
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from evercore_jwt_auth.rest_framework.authentication import JWTAuthentication
from evercore_jwt_auth.rest_framework.permissions import (
    MultiFactorSessionAlive
)

from idvalid_core.rest.permissions import DeviceCookieRequired

from authn.rest.permissions import (
    PlatformPermission,
)

from authn.rest.permissions import HasSecurityCode
from .serializers import (
    SetSerializer,
)

if TYPE_CHECKING:
    from rest_framework.request import Request
    from authn.models import UserMFA


logger = logging.getLogger(__name__)
__all__ = (
    "SecurityCodeViewSet",
)


class SecurityCodeViewSet(GenericViewSet):
    request: "Request"
    authentication_classes = (JWTAuthentication,)
    serializer_class = SetSerializer

    def get_permissions(self):
        action = self.action
        base_perms = (
            DeviceCookieRequired,
            PlatformPermission,
            IsAuthenticated,
            MultiFactorSessionAlive,
        )
        if action == "destroy":
            # update pin
            self.permission_classes = base_perms + (
                HasSecurityCode,
            )
        else:
            self.permission_classes = base_perms
        return super().get_permissions()

    def update(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        instance = request.user.mfa  # type: UserMFA
        instance.remove_security_code()
        return Response(status=status.HTTP_204_NO_CONTENT)
