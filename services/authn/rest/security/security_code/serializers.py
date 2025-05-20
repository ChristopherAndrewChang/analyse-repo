from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from authn.models import SecurityCode
from authn.rest.validators import DigitValidator
from authn.settings import authn_settings

if TYPE_CHECKING:
    from authn.models import User, UserMFA


logger = logging.getLogger(__name__)
__all__ = (
    "SetSerializer",
)


class SetSerializer(serializers.Serializer):
    default_error_messages = {
        "same_pin": _("Cannot be the same as current pin.")
    }
    new_pin = serializers.CharField(
        source="pin",
        max_length=authn_settings.SECURITY_CODE_PIN_LENGTH,
        min_length=authn_settings.SECURITY_CODE_PIN_LENGTH,
        validators=[DigitValidator()]
    )

    def validate_new_pin(self, value: str) -> str:
        mfa = self.context["request"].user.mfa  # type: UserMFA
        if mfa.has_security_code():
            if mfa.security_code.verify(value):
                self.fail("same_pin")
        return value

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user  # type: User
        instance = SecurityCode.objects.create(
            created_by=user,
            **validated_data)
        user.mfa.set_security_code(instance)
        return instance
