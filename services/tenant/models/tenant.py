from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import gettext_lazy as _

from idvalid_core.models import get_subid_model

from tenant_sdk.constants import TENANT_NAME_MAX_LENGTH

if TYPE_CHECKING:
    from typing import Self
    from tenant.models import User


logger = logging.getLogger(__name__)
__all__ = (
    "TenantQuerySet",
    "TenantManager",
    "Tenant",
)


class TenantQuerySet(models.QuerySet):
    def accessible_by_user(self, user_id: int) -> Self:
        return self.filter(
            tenantuser__user_id=user_id,
            tenantuser__is_registered=True,
            tenantuser__is_active=True)


_TenantManagerBase = models.Manager.from_queryset(
    TenantQuerySet
)  # type: type[TenantQuerySet]


class TenantManager(_TenantManagerBase, BaseManager):
    pass


class Tenant(get_subid_model()):
    name = models.CharField(
        _("name"), max_length=TENANT_NAME_MAX_LENGTH)
    is_active = models.BooleanField(
        _("active flag"), default=True)

    created_by_id: int
    created_by = models.ForeignKey(
        "tenant.User", on_delete=models.CASCADE,
        verbose_name=_("created_by")
    )  # type: User
    created = models.DateTimeField(
        _("created"), auto_now_add=True)

    objects = TenantManager()

    def __str__(self):
        return f"{self.name} (ID:{self.pk})"
