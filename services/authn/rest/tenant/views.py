from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from evercore_jwt_auth.rest_framework.authentication import JWTAuthentication
from evercore_jwt_auth.rest_framework.permissions import (
    MultiFactorSessionAlive,
)

from idvalid_core.rest.permissions import DeviceCookieRequired

from authn.rest.permissions import PlatformPermission

from .serializers import TenantSerializer

if TYPE_CHECKING:
    from rest_framework.request import Request


logger = logging.getLogger(__name__)
__all__ = (
    "TenantViewSet",
)


class TenantViewSet(GenericViewSet):
    request: "Request"
    authentication_classes = (JWTAuthentication,)
    permission_classes = (
        DeviceCookieRequired,
        PlatformPermission,
        IsAuthenticated,
        MultiFactorSessionAlive,
    )
    lookup_field = "subid"
    serializer_class = TenantSerializer

    def select(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)
