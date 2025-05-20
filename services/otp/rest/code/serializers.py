from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from evercore.rest.fields import BinaryField

from otp.models import Code
from otp.settings import otp_settings

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "CodeSerializer",
)


class CodeSerializer(serializers.ModelSerializer):
    default_error_messages = {
        "invalid_code": _("Invalid.")
    }
    code = serializers.CharField(
        max_length=otp_settings.DEFAULT_CODE_LENGTH,
        write_only=True)
    signature = BinaryField(read_only=True)

    class Meta:
        model = Code
        fields = (
            'code',
            'signature',
        )

    def validate_code(self, value: str) -> str:
        instance = self.instance  # type: Code
        if not instance.check_code(value):
            self.fail("invalid_code")
        return value

    def update(self, instance: Code, validated_data: dict) -> Code:
        instance.apply()
        return instance
