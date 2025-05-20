from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import gettext_lazy as _

from idvalid_core.models import get_subid_model

if TYPE_CHECKING:
    from tenant.models import Tenant, User


logger = logging.getLogger(__name__)
__all__ = (
    "TenantUserQuerySet",
    "TenantUserManager",
    "TenantUser",
)


class TenantUserQuerySet(models.QuerySet):
    pass


_TenantUserManagerBase = models.Manager.from_queryset(
    TenantUserQuerySet
)  # type: type[TenantUserQuerySet]


class TenantUserManager(_TenantUserManagerBase, BaseManager):
    pass


class TenantUser(get_subid_model()):
    tenant_id: int
    tenant = models.ForeignKey(
        "tenant.Tenant", on_delete=models.CASCADE,
        verbose_name=_("tenant")
    )  # type: Tenant
    user_id: int
    user = models.ForeignKey(
        "tenant.User", on_delete=models.CASCADE,
        verbose_name=_("user")
    )  # type: User

    is_owner = models.BooleanField(
        _("owner status"), default=False)
    is_registered = models.BooleanField(
        _("registered status"), default=False)
    is_active = models.BooleanField(
        _("active status"), default=True)

    date_joined = models.DateTimeField(
        _("date joined"),
        auto_now_add=True)

    objects = TenantUserManager()

    class Meta:
        unique_together = (
            ("tenant", "user"),
        )

    def update_active_status(
            self, value: bool, *,
            save: bool = True):
        self.is_active = value
        if save:
            self.save(update_fields=["is_active"])

    def activate(self, *, save: bool = True):
        self.update_active_status(True, save=save)

    def deactivate(self, *, save: bool = True):
        self.update_active_status(False, save=save)
