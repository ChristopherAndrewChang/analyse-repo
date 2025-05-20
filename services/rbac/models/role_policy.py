from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import gettext_lazy as _

from idvalid_core.models import get_subid_model

if TYPE_CHECKING:
    from rbac.models import Role, Policy


logger = logging.getLogger(__name__)
__all__ = (
    "RolePolicyQuerySet",
    "RolePolicyManager",
    "RolePolicy",
)


class RolePolicyQuerySet(models.QuerySet):
    pass


_RolePolicyManagerBase = models.Manager.from_queryset(
    RolePolicyQuerySet
)  # type: type[RolePolicyQuerySet]


class RolePolicyManager(_RolePolicyManagerBase, BaseManager):
    pass


class RolePolicy(get_subid_model()):
    role_id: int
    role = models.ForeignKey(
        "rbac.Role", on_delete=models.CASCADE,
        verbose_name=_("role")
    )  # type: Role
    policy_id: int
    policy = models.ForeignKey(
        "rbac.Policy", on_delete=models.CASCADE,
    )  # type: Policy

    objects = RolePolicyManager()

    class Meta:
        unique_together = (
            ("role", "policy"),
        )
        verbose_name = _("role policy")
        verbose_name_plural = _("role policies")
