from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from authn.rest.validators import DigitValidator

if TYPE_CHECKING:
    from authn.models import TOTP, User


logger = logging.getLogger(__name__)
__all__ = (
    "ConfirmSerializer",
)


class ConfirmSerializer(serializers.Serializer):
    instance: TOTP | None
    default_error_messages = {
        "invalid_format": _("Invalid format."),
        "incorrect": _("Incorrect.")
    }

    code = serializers.CharField(
        min_length=4, max_length=9,
        validators=[DigitValidator()])

    def validate_code(self, value: str) -> str:
        if not self.instance.verify(value):
            self.fail("incorrect")
        return value

    def update(self, instance: TOTP, validated_data: dict) -> TOTP:
        self.context["request"].user.mfa.set_totp(instance)
        return instance
