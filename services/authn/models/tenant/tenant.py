from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import gettext_lazy as _

from idvalid_core.models import get_subid_model


if TYPE_CHECKING:
    from idvalid_integration.protos.models import tenant_pb2


logger = logging.getLogger(__name__)
__all__ = (
    "TenantQuerySet",
    "TenantManager",
    "Tenant",
)


class TenantQuerySet(models.QuerySet):
    pass


_TenantManagerBase = models.Manager.from_queryset(
    TenantQuerySet
)  # type: type[TenantQuerySet]


class TenantManager(_TenantManagerBase, BaseManager):
    def create_or_update_from_message(
            self, message: tenant_pb2.Tenant) -> Tenant:
        try:
            instance = self.get(pk=message.id)  # type: Tenant
        except self.model.DoesNotExist:
            instance = self.model(pk=message.id)  # type: Tenant
        instance.subid = message.subid
        instance.is_active = message.is_active
        instance.save()
        return instance


class Tenant(get_subid_model()):
    is_active = models.BooleanField(
        _("active flag"))

    objects = TenantManager()
