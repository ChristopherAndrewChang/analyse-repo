from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from evercore_jwt_auth.rest_framework.authentication import JWTStatelessUserAuthentication
from evercore_jwt_auth.rest_framework.permissions import HasSelectedTenant

from tenant.models import TenantUser

from .serializers import TenantUserSerializer

if TYPE_CHECKING:
    from rest_framework.request import Request


logger = logging.getLogger(__name__)
__all__ = (
    "UserViewSet",
)


class UserViewSet(GenericViewSet):
    request: "Request"
    authentication_classes = (JWTStatelessUserAuthentication,)
    permission_classes = (
        IsAuthenticated,
        HasSelectedTenant,
    )
    serializer_class = TenantUserSerializer
    lookup_field = "subid"

    def get_queryset(self):
        filters = {
            "tenant_id": self.request.auth.tenant_id
        }
        action = self.action
        if action == "deactivate":
            filters["is_active"] = True
        elif action == "activate":
            filters["is_active"] = False
        return TenantUser.objects.filter(
            **filters
        ).select_related("user")

    def list(self, request: Request, *args, **kwargs) -> Response:
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def deactivate(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()  # type: TenantUser
        instance.deactivate()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def activate(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()  # type: TenantUser
        instance.activate()
        return Response(status=status.HTTP_204_NO_CONTENT)
