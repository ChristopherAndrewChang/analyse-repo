from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from otp.models import Otp
from otp.settings import otp_settings

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "ApplySerializer",
)


class ApplySerializer(serializers.ModelSerializer):
    default_error_messages = {
        "invalid_pin": _("Invalid.")
    }

    pin = serializers.CharField(
        max_length=otp_settings.DEFAULT_PIN_LENGTH,
        min_length=otp_settings.DEFAULT_PIN_LENGTH,
        write_only=True)

    class Meta:
        model = Otp
        fields = (
            "id",
            "token",
            "pin",)
        extra_kwargs = {
            "id": {"read_only": True, "source": "subid"},
            "token": {"read_only": True}
        }

    def validate_pin(self, value: str) -> str:
        instance = self.instance  # type: Otp
        if not instance.verify(value):
            self.fail("invalid_pin")
        return value

    def update(self, instance: Otp, validated_data: dict) -> Otp:
        instance.apply()
        return instance
