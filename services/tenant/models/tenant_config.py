from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from tenant.models import Tenant


logger = logging.getLogger(__name__)
__all__ = (
    "TenantConfigQuerySet",
    "TenantConfigManager",
    "TenantConfig",
)


class TenantConfigQuerySet(models.QuerySet):
    pass


_TenantConfigManagerBase = models.Manager.from_queryset(
    TenantConfigQuerySet
)  # type: type[TenantConfigQuerySet]


class TenantConfigManager(_TenantConfigManagerBase, BaseManager):
    pass


class TenantConfig(models.Model):
    tenant_id: int
    tenant = models.OneToOneField(
        "tenant.Tenant", on_delete=models.CASCADE,
        related_name="config",
        primary_key=True,
        verbose_name=_("tenant")
    )  # type: Tenant

    objects = TenantConfigManager()
