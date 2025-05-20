from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

# from evercore import rest

from account.models import Enrollment, Account, constants

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = ("CreateSerializer",)


class CreateSerializer(serializers.Serializer):
    default_error_messages = {
        "invalid_param": _("Invalid."),
    }
    state = serializers.CharField()
    otp_id = serializers.CharField()
    otp_token = serializers.CharField()

    password = serializers.CharField(
        validators=[validate_password])
    username = serializers.CharField(
        validators=[
            Account.username_validator,
            UniqueValidator(
                Account.objects.all(),
                message=_("Already used.")
            )
        ],
        max_length=constants.ACCOUNT_USERNAME_MAX_LENGTH)
    name = serializers.CharField(
        max_length=constants.ACCOUNT_NAME_MAX_LENGTH)
    client_id = serializers.CharField()

    def validate_state(self, value: str):
        enrollment = self.context['enrollment']  # type: Enrollment
        if not enrollment.check_state(value):
            self.fail("invalid_param")
        return None

    def validate_otp_id(self, value: str):
        enrollment = self.context['enrollment']  # type: Enrollment
        if enrollment.otp_token.subid != value:
            self.fail("invalid_param")

    def validate_otp_token(self, value: str):
        enrollment = self.context['enrollment']  # type: Enrollment
        # todo: use compare_digest
        if enrollment.otp_token.token != value:
            self.fail("invalid_param")

    def update(self, instance: Enrollment, validated_data: dict) -> Account:
        raise Exception(instance, validated_data)

    def create(self, validated_data):
        validated_data.pop("state")
        validated_data.pop("otp_id")
        validated_data.pop("otp_token")
        validated_data["email"] = self.context["enrollment"].email.address
        return Account.objects.create(**validated_data)
