from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from rbac.models import Policy, Permission


logger = logging.getLogger(__name__)
__all__ = (
    "PolicyPermissionQuerySet",
    "PolicyPermissionManager",
    "PolicyPermission",
)


class PolicyPermissionQuerySet(models.QuerySet):
    pass


_PolicyPermissionManagerBase = models.Manager.from_queryset(
    PolicyPermissionQuerySet
)  # type: type[PolicyPermissionQuerySet]


class PolicyPermissionManager(_PolicyPermissionManagerBase, BaseManager):
    pass


class PolicyPermission(models.Model):
    policy_id: int
    policy = models.ForeignKey(
        "rbac.Policy", on_delete=models.CASCADE,
        verbose_name=_("policy")
    )  # type: Policy
    permission_id: int
    permission = models.ForeignKey(
        "rbac.Permission", on_delete=models.CASCADE,
        verbose_name=_("permission")
    )  # type: Permission

    objects = PolicyPermissionManager()

    class Meta:
        unique_together = (
            ("policy", "permission"),
        )
        verbose_name = _("policy permission")
        verbose_name_plural = _("policy permissions")
