from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from evercore_jwt_auth.rest_framework.authentication import JWTStatelessUserAuthentication
from evercore_jwt_auth.rest_framework.permissions import HasSelectedTenant

from tenant.models import Tenant

from .serializers import ProfileSerializer

if TYPE_CHECKING:
    from rest_framework.request import Request


logger = logging.getLogger(__name__)
__all__ = (
    "ProfileViewSet",
)


class ProfileViewSet(GenericViewSet):
    request: "Request"
    authentication_classes = (JWTStatelessUserAuthentication,)
    permission_classes = (
        IsAuthenticated,
        HasSelectedTenant,
    )
    serializer_class = ProfileSerializer

    def get_queryset(self):
        return Tenant.objects.accessible_by_user(
            self.request.user.pk)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        filter_kwargs = {"id": self.request.auth.tenant_id}
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        # self.check_object_permissions(self.request, obj)

        return obj

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
