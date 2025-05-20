from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from authn.models import (
    MobileOTP,
)

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "ListSerializer",
    "VerifySerializer",
)


class ListSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="subid")

    class Meta:
        model = MobileOTP
        fields = (
            "id",
            "valid_until"
        )


class VerifySerializer(serializers.Serializer):
    instance: MobileOTP

    default_error_messages = {
        "invalid_pin": _("Invalid.")
    }
    pin = serializers.CharField()

    def validate_pin(self, value):
        if not self.instance.verify(value):
            self.fail("invalid_pin")
        return None
