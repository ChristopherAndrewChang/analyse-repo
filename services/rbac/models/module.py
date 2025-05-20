from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import gettext_lazy as _

from idvalid_core.models import get_subid_model

from rbac_sdk.constants import (
    MODULE_CODENAME_MAX_LENGTH,
    MODULE_NAME_MAX_LENGTH,
)

if TYPE_CHECKING:
    from rbac.models import Service


logger = logging.getLogger(__name__)
__all__ = (
    "ModuleQuerySet",
    "ModuleManager",
    "Module",
)


class ModuleQuerySet(models.QuerySet):
    pass


_ModuleManagerBase = models.Manager.from_queryset(
    ModuleQuerySet
)  # type: type[ModuleQuerySet]


class ModuleManager(_ModuleManagerBase, BaseManager):
    pass


class Module(get_subid_model()):
    service_id: int
    service = models.ForeignKey(
        "rbac.Service", on_delete=models.CASCADE,
        related_name="modules",
        verbose_name=_("service")
    )  # type: Service
    codename = models.CharField(
        _("codename"),
        max_length=MODULE_CODENAME_MAX_LENGTH)
    name = models.CharField(
        _("name"),
        max_length=MODULE_NAME_MAX_LENGTH)
    description = models.TextField(
        _("description"), null=True, blank=True)

    is_active = models.BooleanField(
        _("active status"), default=True)

    created_time = models.DateTimeField(
        _("created time"), auto_now_add=True)

    objects = ModuleManager()

    class Meta:
        unique_together = (
            ("service", "codename"),
        )
        verbose_name = _("module")
        verbose_name_plural = _("modules")
