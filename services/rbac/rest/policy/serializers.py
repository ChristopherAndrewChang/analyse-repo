from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from rest_framework import serializers

from rbac.models import Policy

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "PolicySerializer",
)


class PolicySerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="subid")
    selected = serializers.ReadOnlyField()
    object_id = serializers.ReadOnlyField()

    class Meta:
        model = Policy
        fields = (
            "id",
            "selected",
            "object_id",

            "name",
            "description",
            "is_active",
        )
