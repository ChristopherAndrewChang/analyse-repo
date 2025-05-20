from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.utils.functional import cached_property

from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import GenericViewSet

from rbac.models import Role

if TYPE_CHECKING:
    from rest_framework.request import Request


logger = logging.getLogger(__name__)
__all__ = (
    "RoleReferenceBase",
)


class RoleReferenceBase(GenericViewSet):
    request: "Request"
    ref_lookup_field = "subid"
    ref_lookup_url_kwarg = "role"

    def get_reference(self) -> Role:
        return get_object_or_404(
            Role.objects.filter(
                tenant_id=self.request.auth.tenant_id
            ),
            **{
                self.ref_lookup_field: self.kwargs[self.ref_lookup_url_kwarg]
            }
        )

    @cached_property
    def reference(self) -> Role:
        return self.get_reference()
