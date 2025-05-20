from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.utils.translation import gettext_lazy as _

from evercore_grpc.framework import serializers

from idvalid_integration.rpc.enrollment.email import ConfirmResponse

from enrollment.models import constants

if TYPE_CHECKING:
    from enrollment.models import Otp


logger = logging.getLogger(__name__)
__all__ = ("GetEmailSerializer", "ConfirmSerializer",)


class GetEmailSerializer(serializers.Serializer):
    state = serializers.CharField(
        max_length=constants.STATE_LENGTH,
        write_only=True)

    def validate_state(self, value: str) -> str:
        instance = self.instance  # type: Otp
        if not instance.check_state(value):
            self.fail('invalid_param')
        return value


class ConfirmSerializer(serializers.Serializer):
    default_error_messages = {
        "invalid_param": _("Invalid.")
    }

    device_id = serializers.CharField(
        max_length=constants.DEVICE_ID_LENGTH,
        write_only=True)
    user_agent = serializers.CharField(
        write_only=True)
    signature = serializers.BinaryField(
        trim_whitespace=False,
        write_only=True)
    email = serializers.EmailField(
        write_only=True)
    success = serializers.ReadOnlyField(
        source="is_confirmed")

    class Meta:
        read_proto_class = ConfirmResponse

    def validate_device_id(self, value: str) -> str:
        instance = self.instance  # type: Otp
        if not instance.device_id == value:
            self.fail('invalid_param')
        return value

    def validate_user_agent(self, value: str) -> str:
        instance = self.instance  # type: Otp
        if not instance.user_agent == value:
            self.fail('invalid_param')
        return value

    def validate_signature(self, value: bytes) -> bytes:
        instance = self.instance  # type: Otp
        if not instance.verify(value):
            self.fail('invalid_param')
        return value

    def validate_email(self, value: str) -> str:
        instance = self.instance  # type: Otp
        if not instance.enrollment.email == value:
            self.fail('invalid_param')
        return value

    def update(self, instance: Otp, validated_data: dict) -> Otp:
        instance.confirm()
        return instance
