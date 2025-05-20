from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import gettext_lazy as _

from idvalid_core.models import get_subid_model

from rbac_sdk.constants import ROLE_NAME_MAX_LENGTH

if TYPE_CHECKING:
    from rbac.models import Tenant


logger = logging.getLogger(__name__)
__all__ = (
    "RoleQuerySet",
    "RoleManager",
    "Role",
)


class RoleQuerySet(models.QuerySet):
    pass


_RoleManagerBase = models.Manager.from_queryset(
    RoleQuerySet
)  # type: type[RoleQuerySet]


class RoleManager(_RoleManagerBase, BaseManager):
    pass


class Role(get_subid_model()):
    tenant_id: int
    tenant = models.ForeignKey(
        "rbac.Tenant", on_delete=models.CASCADE,
        related_name="roles",
        verbose_name=_("tenant")
    )  # type: Tenant
    name = models.CharField(
        _("name"),
        max_length=ROLE_NAME_MAX_LENGTH)
    description = models.TextField(
        _("description"),
        null=True, blank=True)
    policies = models.ManyToManyField(
        "rbac.Policy",
        related_name="roles",
        through="rbac.RolePolicy",
        through_fields=("role", "policy"))
    users = models.ManyToManyField(
        "rbac.User",
        related_name="roles",
        through="rbac.RoleUser",
        through_fields=("role", "user"))

    is_active = models.BooleanField(
        _("active statue"), default=True)

    created_time = models.DateTimeField(
        _("created time"), auto_now_add=True)

    objects = RoleManager()

    def __str__(self):
        return f"{self.name} (ID: {self.pk}, Tenant ID: {self.tenant_id})"

    class Meta:
        verbose_name = _("role")
        verbose_name_plural = _("roles")
