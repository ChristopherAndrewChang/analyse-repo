from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from evercore_jwt_auth.rest_framework.authentication import JWTStatelessUserAuthentication
from evercore_jwt_auth.rest_framework.permissions import HasSelectedTenant

from rbac.models import RolePolicy

from .serializers import RolePolicySerializer

if TYPE_CHECKING:
    from rest_framework.request import Request


logger = logging.getLogger(__name__)
__all__ = (
    "RolePolicyViewSet",
)


class RolePolicyViewSet(
        CreateModelMixin,
        DestroyModelMixin,
        GenericViewSet):
    request: "Request"
    authentication_classes = (JWTStatelessUserAuthentication,)
    permission_classes = (
        IsAuthenticated,
        HasSelectedTenant,
    )
    serializer_class = RolePolicySerializer
    lookup_field = "subid"

    def get_queryset(self):
        return RolePolicy.objects.filter(
            role__tenant_id=self.request.auth.tenant_id)
