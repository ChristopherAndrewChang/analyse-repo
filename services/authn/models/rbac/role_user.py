from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from idvalid_integration.protos.models import rbac_pb2
    from authn.models import User


logger = logging.getLogger(__name__)
__all__ = (
    "RoleUserQuerySet",
    "RoleUserManager",
    "RoleUser",
)


class RoleUserQuerySet(models.QuerySet):
    pass


_RoleUserManagerBase = models.Manager.from_queryset(
    RoleUserQuerySet
)  # type: type[RoleUserQuerySet]


class RoleUserManager(_RoleUserManagerBase, BaseManager):
    def create_or_update_from_message(
            self, message: rbac_pb2.RoleUser) -> RoleUser:
        try:
            instance = self.get(
                tenant_id=message.tenant_id,
                role_id=message.role_id,
                user_id=message.user_id
            )  # type: RoleUser
        except self.model.DoesNotExist:
            instance = self.model(
                tenant_id=message.tenant_id,
                role_id=message.role_id,
                user_id=message.user_id
            )
        instance.save()
        return instance

    def delete_from_message(
            self, message: rbac_pb2.RoleUser) -> int:
        return self.filter(
            tenant_id=message.tenant_id,
            role_id=message.role_id,
            user_id=message.user_id
        ).delete()


class RoleUser(models.Model):
    tenant_id = models.PositiveBigIntegerField(
        _("tenant id"))
    role_id = models.PositiveBigIntegerField(
        _("role id"))
    user_id: int
    user = models.ForeignKey(
        "authn.User", on_delete=models.CASCADE,
        verbose_name=_("user")
    )  # type: User

    objects = RoleUserManager()

    class Meta:
        unique_together = (
            ("tenant_id", "role_id", "user"),
        )
