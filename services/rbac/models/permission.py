from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import gettext_lazy as _

from idvalid_core.models import get_subid_model

from rbac_sdk.constants import (
    PERMISSION_CODENAME_MAX_LENGTH,
    PERMISSION_NAME_MAX_LENGTH,
)

if TYPE_CHECKING:
    from rbac.models import Module


logger = logging.getLogger(__name__)
__all__ = (
    "PermissionQuerySet",
    "PermissionManager",
    "Permission",
)


class PermissionQuerySet(models.QuerySet):
    pass


_PermissionManagerBase = models.Manager.from_queryset(
    PermissionQuerySet
)  # type: type[PermissionQuerySet]


class PermissionManager(_PermissionManagerBase, BaseManager):
    pass


class Permission(get_subid_model()):
    module_id: int
    module = models.ForeignKey(
        "rbac.Module", on_delete=models.CASCADE,
        related_name="permissions",
        verbose_name=_("module")
    )  # type: Module
    codename = models.CharField(
        _("codename"),
        max_length=PERMISSION_CODENAME_MAX_LENGTH)
    name = models.CharField(
        _("name"),
        max_length=PERMISSION_NAME_MAX_LENGTH)
    description = models.TextField(
        _("description"), null=True, blank=True)

    is_active = models.BooleanField(
        _("active status"), default=True)

    created_time = models.DateTimeField(
        _("created time"), auto_now_add=True)

    objects = PermissionManager()

    def __str__(self):
        module = self.module
        service = module.service
        return f"{service.codename}.{module.codename}.{self.codename} ({self.name})"

    class Meta:
        unique_together = (
            ("module", "codename"),
        )
        verbose_name = _("permission")
        verbose_name_plural = _("permissions")
