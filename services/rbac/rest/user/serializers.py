from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from rest_framework import serializers

from rbac.models import User

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "UserSerializer",
)


class UserSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="subid")
    is_available = serializers.ReadOnlyField()
    selected = serializers.ReadOnlyField()
    object_id = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = (
            "id",
            "is_available",
            "selected",
            "object_id",

            "name",
            "is_active",
        )
