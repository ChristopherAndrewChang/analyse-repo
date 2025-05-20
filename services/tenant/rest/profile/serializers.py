from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from rest_framework import serializers

from tenant.models import Tenant

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "ProfileSerializer",
)


class ProfileSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="subid")

    class Meta:
        model = Tenant
        fields = (
            "id",
            "name",
            "is_active",
        )
        read_only_fields = ("is_active",)
