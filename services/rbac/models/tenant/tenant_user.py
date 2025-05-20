from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from idvalid_integration.protos.models import tenant_pb2
    from rbac.models import Tenant, User


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
    def create_or_update_from_message(
            self, message: tenant_pb2.TenantUser) -> TenantUser:
        try:
            instance = self.get(
                tenant_id=message.tenant_id, user_id=message.user_id
            )  # type: TenantUser
        except self.model.DoesNotExist:
            instance = self.model(
                tenant_id=message.tenant_id, user_id=message.user_id
            )  # type: TenantUser
        instance.is_owner = message.is_owner
        instance.is_registered = message.is_registered
        instance.is_active = message.is_active
        instance.save()
        return instance

    def delete_from_message(
            self, message: tenant_pb2.TenantUser) -> int:
        return self.filter(
            tenant_id=message.tenant_id,
            user_id=message.user_id,
        ).delete()


class TenantUser(models.Model):
    tenant_id: int
    tenant = models.ForeignKey(
        "rbac.Tenant", on_delete=models.CASCADE,
        verbose_name=_("tenant")
    )  # type: Tenant
    user_id: int
    user = models.ForeignKey(
        "rbac.User", on_delete=models.CASCADE,
        verbose_name=_("user")
    )  # type: User

    is_owner = models.BooleanField(
        _("owner status"), default=False)
    is_registered = models.BooleanField(
        _("registered status"), default=False)
    is_active = models.BooleanField(
        _("active status"), default=True)

    objects = TenantUserManager()

    class Meta:
        unique_together = (
            ("tenant", "user"),
        )
