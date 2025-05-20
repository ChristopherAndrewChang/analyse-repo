from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from rest_framework import serializers

from tenant.models import User, TenantUser

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "UserSerializer",
    "TenantUserSerializer",
)


class UserSerializer(serializers.ModelSerializer):
    # id = serializers.ReadOnlyField(source="subid")

    class Meta:
        model = User
        fields = (
            # "id",
            "name",
            "is_active")


class TenantUserSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="subid")
    user = UserSerializer(read_only=True)

    class Meta:
        model = TenantUser
        fields = (
            "id",
            "user",
            "is_owner",
            "is_registered",
            "is_active",
        )
