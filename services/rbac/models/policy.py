from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import gettext_lazy as _

from idvalid_core.models import get_subid_model

from rbac_sdk.constants import POLICY_NAME_MAX_LENGTH

if TYPE_CHECKING:
    from typing import Self, Optional


logger = logging.getLogger(__name__)
__all__ = (
    "PolicyQuerySet",
    "PolicyManager",
    "Policy",
)


class PolicyQuerySet(models.QuerySet):
    def fetch_role(self, role_id: int) -> Self:
        return self.alias(
            _rolepolicy_rel=models.FilteredRelation(
                "rolepolicy",
                condition=models.Q(
                    rolepolicy__role_id=role_id,
                )
            )
        )

    def filter_role(
            self, role_id: int, *,
            selected: Optional[bool] = None) -> Self:
        queryset = self.fetch_role(role_id).annotate(
            selected=models.ExpressionWrapper(
                models.Q(_rolepolicy_rel__isnull=False),
                output_field=models.BooleanField()
            ),
            object_id=models.F("_rolepolicy_rel__subid")
        )
        if selected is None:
            return queryset.filter(
                models.Q(is_active=True) |
                models.Q(selected=True)
            )
        elif selected:
            return queryset.filter(selected=True)
        else:
            return queryset.filter(
                is_active=True,
                selected=False)


_PolicyManagerBase = models.Manager.from_queryset(
    PolicyQuerySet
)  # type: type[PolicyQuerySet]


class PolicyManager(_PolicyManagerBase, BaseManager):
    pass


class Policy(get_subid_model()):
    name = models.CharField(
        _("name"),
        max_length=POLICY_NAME_MAX_LENGTH)
    description = models.TextField(
        _("description"),
        null=True, blank=True)
    permissions = models.ManyToManyField(
        "rbac.Permission",
        related_name="policies",
        through="rbac.PolicyPermission",
        through_fields=("policy", "permission")
    )

    is_active = models.BooleanField(
        _("active status"), default=True)

    created_time = models.DateTimeField(
        _("created time"), auto_now_add=True)

    objects = PolicyManager()

    def __str__(self) -> str:
        return f"{self.name} (ID:{self.pk})"

    class Meta:
        verbose_name = _("policy")
        verbose_name_plural = _("policies")
