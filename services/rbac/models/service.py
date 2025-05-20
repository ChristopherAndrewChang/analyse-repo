from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import gettext_lazy as _

from idvalid_core.models import get_subid_model

from rbac_sdk.constants import (
    SERVICE_CODENAME_MAX_LENGTH,
    SERVICE_NAME_MAX_LENGTH,
)

if TYPE_CHECKING:
    from rbac.models import ModuleManager


logger = logging.getLogger(__name__)
__all__ = (
    "ServiceQuerySet",
    "ServiceManager",
    "Service",
)


class ServiceQuerySet(models.QuerySet):
    pass


_ServiceManagerBase = models.Manager.from_queryset(
    ServiceQuerySet
)  # type: type[ServiceQuerySet]


class ServiceManager(_ServiceManagerBase, BaseManager):
    pass


class Service(get_subid_model()):
    modules: ModuleManager

    codename = models.CharField(
        _("codename"), unique=True,
        max_length=SERVICE_CODENAME_MAX_LENGTH)
    name = models.CharField(
        _("name"),
        max_length=SERVICE_NAME_MAX_LENGTH)
    description = models.TextField(
        _("description"), null=True, blank=True)

    is_active = models.BooleanField(
        _("active status"), default=True)

    created_time = models.DateTimeField(
        _("created time"), auto_now_add=True)

    objects = ServiceManager()

    def __str__(self):
        return f"{self.codename} (ID: {self.pk})"

    class Meta:
        verbose_name = _("service")
        verbose_name_plural = _("services")
