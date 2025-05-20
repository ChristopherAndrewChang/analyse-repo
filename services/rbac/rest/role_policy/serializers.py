from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from evercore.rest.relations import SlugRelatedField

from rbac.models import Role, Policy, RolePolicy

if TYPE_CHECKING:
    from rbac.models import RoleQuerySet, PolicyQuerySet


logger = logging.getLogger(__name__)
__all__ = (
    "RolePolicySerializer",
)


class RolePolicySerializer(serializers.Serializer):
    class Meta:
        validators = [
            UniqueTogetherValidator(
                RolePolicy.objects.all(),
                ("role", "policy"),
                message=_("Policy already added to this role.")
            )
        ]

    id = serializers.ReadOnlyField(source="subid")
    role = SlugRelatedField(
        slug_field="subid",
        queryset=Role.objects.all(),
        filter_func="filter_role",
        write_only=True)
    policy = SlugRelatedField(
        slug_field="subid",
        queryset=Policy.objects.filter(is_active=True),
        # filter_func="filter_policy",
        write_only=True)

    def filter_role(self, queryset: RoleQuerySet) -> RoleQuerySet:
        request = self.context["request"]
        return queryset.filter(tenant_id=request.auth.tenant_id)

    def create(self, validated_data: dict) -> RolePolicy:
        return RolePolicy.objects.create(**validated_data)
