from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import gettext_lazy as _

from idvalid_core.models import get_subid_model

if TYPE_CHECKING:
    from rbac.models import User, Role


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
    pass


class RoleUser(get_subid_model()):
    role_id: int
    role = models.ForeignKey(
        "rbac.role", on_delete=models.CASCADE,
        verbose_name=_("role")
    )  # type: Role
    user_id: int
    user = models.ForeignKey(
        "rbac.User", on_delete=models.CASCADE,
        verbose_name=_("user")
    )  # type: User

    objects = RoleUserManager()

    class Meta:
        unique_together = (
            ("role", "user"),
        )
        verbose_name = _("role user")
        verbose_name_plural = _("role users")
