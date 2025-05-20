from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from rest_framework.response import Response

from evercore_jwt_auth.rest_framework.authentication import JWTStatelessUserAuthentication

from tenant.models import Tenant

if TYPE_CHECKING:
    from rest_framework.request import Request


logger = logging.getLogger(__name__)
__all__ = (
    "TenantViewSet",
)


class TenantViewSet(GenericViewSet):
    request: "Request"
    authentication_classes = (JWTStatelessUserAuthentication,)
    permission_classes = (
        IsAuthenticated,
    )

    def get_queryset(self):
        return Tenant.objects.accessible_by_user(
            self.request.user.id)

    def list(self, request: Request, *args, **kwargs) -> Response:
        queryset = self.filter_queryset(
            self.get_queryset()
        ).values(
            "subid",
            "name",
            "is_active",
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(page)

        return Response(queryset)
