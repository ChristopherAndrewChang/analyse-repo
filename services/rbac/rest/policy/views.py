from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from rest_framework.mixins import (
    ListModelMixin,
)
from rest_framework.permissions import IsAuthenticated

from evercore_jwt_auth.rest_framework.authentication import JWTStatelessUserAuthentication
from evercore_jwt_auth.rest_framework.permissions import HasSelectedTenant

from rbac.models import Policy
from rbac.rest.views import RoleReferenceBase

from .serializers import PolicySerializer

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "PolicyViewSet",
)


class PolicyViewSet(ListModelMixin, RoleReferenceBase):
    authentication_classes = (JWTStatelessUserAuthentication,)
    permission_classes = (
        IsAuthenticated,
        HasSelectedTenant,
    )
    serializer_class = PolicySerializer

    def get_queryset(self):
        return Policy.objects.filter_role(
            role_id=self.reference.pk,
            selected=None)
