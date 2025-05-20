from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from rest_framework import serializers

from rbac.models import Role

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "RoleSerializer",
)


class RoleSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="subid")

    class Meta:
        model = Role
        fields = (
            "id",
            "name",
            "description",
            "is_active",
        )
        read_only_fields = ("is_active",)
