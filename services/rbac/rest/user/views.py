from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from rest_framework.mixins import (
    ListModelMixin,
)
from rest_framework.permissions import IsAuthenticated

from evercore_jwt_auth.rest_framework.authentication import JWTStatelessUserAuthentication
from evercore_jwt_auth.rest_framework.permissions import HasSelectedTenant

from rbac.models import User
from rbac.rest.views import RoleReferenceBase

from .serializers import UserSerializer

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "UserViewSet",
)


class UserViewSet(ListModelMixin, RoleReferenceBase):
    authentication_classes = (JWTStatelessUserAuthentication,)
    permission_classes = (
        IsAuthenticated,
        HasSelectedTenant,
    )
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter_role(
            tenant_id=self.request.auth.tenant_id,
            role_id=self.reference.pk,
            selected=None)
