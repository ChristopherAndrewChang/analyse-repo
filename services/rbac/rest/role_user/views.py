from __future__ import annotations
from typing import TYPE_CHECKING

import logging

# from rest_framework import status
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
# from rest_framework.response import Response

from evercore_jwt_auth.rest_framework.authentication import JWTStatelessUserAuthentication
from evercore_jwt_auth.rest_framework.permissions import HasSelectedTenant

from rbac.models import RoleUser

from .serializers import RoleUserSerializer

if TYPE_CHECKING:
    from rest_framework.request import Request


logger = logging.getLogger(__name__)
__all__ = (
    "RoleUserViewSet",
)


class RoleUserViewSet(
        CreateModelMixin,
        DestroyModelMixin,
        GenericViewSet):
    request: "Request"
    authentication_classes = (JWTStatelessUserAuthentication,)
    permission_classes = (
        IsAuthenticated,
        HasSelectedTenant,
    )
    serializer_class = RoleUserSerializer
    lookup_field = "subid"

    def get_queryset(self):
        return RoleUser.objects.filter(
            role__tenant_id=self.request.auth.tenant_id)
