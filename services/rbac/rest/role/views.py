from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from rest_framework import status
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from evercore_jwt_auth.rest_framework.authentication import JWTStatelessUserAuthentication
from evercore_jwt_auth.rest_framework.permissions import HasSelectedTenant

from rbac.models import Role

from .serializers import RoleSerializer

if TYPE_CHECKING:
    from rest_framework.request import Request


logger = logging.getLogger(__name__)
__all__ = (
    "RoleViewSet",
)


class RoleViewSet(
        ListModelMixin,
        CreateModelMixin,
        RetrieveModelMixin,
        UpdateModelMixin,
        GenericViewSet):
    request: "Request"
    authentication_classes = (JWTStatelessUserAuthentication,)
    permission_classes = (
        IsAuthenticated,
        HasSelectedTenant,
    )
    serializer_class = RoleSerializer
    lookup_field = "subid"

    def get_queryset(self):
        return Role.objects.filter(
            tenant_id=self.request.auth.tenant_id)

    def perform_create(self, serializer):
        serializer.save(
            tenant_id=self.request.auth.tenant_id)
