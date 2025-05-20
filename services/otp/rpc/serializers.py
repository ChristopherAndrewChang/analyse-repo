from __future__ import annotations
from typing import TYPE_CHECKING

import contextlib
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from evercore_grpc.framework import serializers
from idvalid_integration.rpc.otp.code import (
    CreateRequest, CreateResponse)

from otp.integration.rpc import generate_key_pair
from otp.models import Code, Issuer, Usage, Recipient, constants

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "EmailSerializer",
    "PhoneNumberSerializer",
    "AppSerializer",
    "CodeSerializer",
)


class EmailSerializer(serializers.Serializer):
    value = serializers.EmailField(max_length=128)

    class Meta:
        write_proto_class = CreateRequest.EmailOtp

    def validate_value(self, value: str) -> str | Recipient:
        with contextlib.suppress(ObjectDoesNotExist):
            return Recipient.objects.get(
                type__name="email", contact=value)
        return value


class PhoneNumberSerializer(serializers.Serializer):
    value = serializers.PhoneNumberField()

    class Meta:
        write_proto_class = CreateRequest.SmsOtp

    def validate_value(self, value: str) -> str | Recipient:
        with contextlib.suppress(ObjectDoesNotExist):
            return Recipient.objects.get(
                type__name="phone", contact=value)
        return value


class AppSerializer(serializers.Serializer):
    value = serializers.CharField(max_length=128)

    class Meta:
        write_proto_class = CreateRequest.AppOtp

    def validate_value(self, value: str) -> str | Recipient:
        with contextlib.suppress(ObjectDoesNotExist):
            return Recipient.objects.get(
                type__name="app", contact=value)
        return value


class CodeSerializer(serializers.ModelSerializer):
    default_error_messages = {
        "invalid_ref_id": "Unable to suppress due to invalid 'ref_id'.",
        "invalid_suppress_state": "Unable to suppress due to state condition.",
    }
    recipient_type_mapping = {
        "email": "email",
        "sms": "phone",
        "app": "app",
    }

    key = serializers.BinaryField(
        read_only=True,
        source="public_key")

    expires_in = serializers.DurationField(
        write_only=True, allow_null=True)
    recipient = serializers.OneOfField(
        write_only=True,
        fields_map={
            "email": EmailSerializer(),
            "sms": PhoneNumberSerializer(),
            "app": AppSerializer(),
        })
    usage = serializers.CharField(
        write_only=True,
        max_length=constants.USAGE_NAME_LENGTH)
    issuer = serializers.CharField(
        write_only=True,
        max_length=constants.ISSUER_NAME_LENGTH)
    # suppress = serializers.CharField(
    #     write_only=True)
    suppress = serializers.SlugRelatedField(
        required=False,
        slug_field="subid",
        queryset=Code.objects.all(),
        write_only=True)

    class Meta:
        model = Code
        write_proto_class = CreateRequest
        read_proto_class = CreateResponse
        fields = (
            # read only
            "id",
            "expires",
            "key",

            # write only
            "expires_in",
            "usage",
            "issuer",
            "recipient",
            "ref_id",
            "device_id",
            "suppress"
        )
        extra_kwargs = {
            "id": {"source": "subid"},
            "ref_id": {"write_only": True},
            "device_id": {"write_only": True},
        }
        read_only_fields = ("id", "expires")

    def validate_usage(self, value: str) -> str | Usage:
        with contextlib.suppress(ObjectDoesNotExist):
            return Usage.objects.get(name=value)
        return value

    def validate_issuer(self, value: str) -> str | Issuer:
        with contextlib.suppress(ObjectDoesNotExist):
            return Issuer.objects.get(name=value)
        return value

    def validate(self, attrs):
        if suppress := attrs.get("suppress"):
            if suppress.ref_id != attrs["ref_id"]:
                raise serializers.ValidationError({
                    "suppress": self.error_messages["invalid_ref_id"]})
            if not suppress.allow_suppression():
                raise serializers.ValidationError({
                    "suppress": self.error_messages["invalid_suppress_state"]
                })
        return attrs

    def create(self, validated_data):
        try:
            validated_data["suppress"].suppress()
        except KeyError:
            pass

        usage = validated_data["usage"]
        issuer = validated_data["issuer"]
        recipient_type, recipient = validated_data["recipient"]
        recipient = recipient["value"]
        key_pair = generate_key_pair()
        data = {
            "expires": timezone.now() + validated_data["expires_in"],
            "recipient": (
                recipient
                if isinstance(recipient, Recipient) else
                Recipient.objects.create(
                    type=self.recipient_type_mapping[recipient_type],
                    contact=recipient
                )
            ),
            "usage": (
                usage
                if isinstance(usage, Usage) else
                Usage.objects.create(name=usage)
            ),
            "issuer": (
                issuer
                if isinstance(issuer, Issuer) else
                Issuer.objects.create(name=issuer)
            ),
            "ref_id": validated_data["ref_id"],
            "device_id": validated_data["device_id"],
            "key": key_pair.pair.private_key
        }
        instance = super().create(data)
        instance.public_key = key_pair.pair.public_key
        return instance


class CodeConfirmSerializer(serializers.ModelSerializer):
    usage = serializers.CharField(
        write_only=True,
        max_length=constants.USAGE_NAME_LENGTH)

    class Meta:
        model = Code
        fields = (
            "ref_id",
            "usage",
            "success",
        )
        extra_kwargs = {
            "ref_id": {"write_only": True},
            "success": {
                "source": "confirmed",
                "read_only": True,
            },
        }

    def update(self, instance: Code, validated_data: dict) -> Code:
        if instance.ref_id != validated_data["ref_id"]:
            return instance
        if instance.usage.name != validated_data["usage"]:
            return instance
        instance.confirm()
        return instance
