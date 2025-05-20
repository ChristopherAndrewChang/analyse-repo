from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from evercore.rest.relations import SlugRelatedField

from rbac.models import User, Role, RoleUser

if TYPE_CHECKING:
    from rbac.models import UserQuerySet, RoleQuerySet


logger = logging.getLogger(__name__)
__all__ = (
    "RoleUserSerializer",
)


class RoleUserSerializer(serializers.Serializer):
    class Meta:
        validators = [
            UniqueTogetherValidator(
                RoleUser.objects.all(),
                ("user", "role"),
                message=_("Role already assigned to this user.")
            )
        ]

    id = serializers.ReadOnlyField(source="subid")
    user = SlugRelatedField(
        slug_field="subid",
        queryset=User.objects.all(),
        filter_func="filter_user",
        write_only=True)
    role = SlugRelatedField(
        slug_field="subid",
        queryset=Role.objects.all(),
        filter_func="filter_role",
        write_only=True)

    def filter_user(self, queryset: UserQuerySet) -> UserQuerySet:
        request = self.context["request"]
        return queryset.filter_tenant(request.auth.tenant_id)

    def filter_role(self, queryset: RoleQuerySet) -> RoleQuerySet:
        request = self.context["request"]
        return queryset.filter(tenant_id=request.auth.tenant_id)

    def create(self, validated_data: dict) -> RoleUser:
        return RoleUser.objects.create(**validated_data)
