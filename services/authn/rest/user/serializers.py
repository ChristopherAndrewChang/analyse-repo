from __future__ import annotations
from typing import TYPE_CHECKING

import logging
import struct

from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from django.utils.crypto import constant_time_compare

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from evercore.rest import Base64Field

from authn.models import (
    Enrollment,
    User,
    UserProfile,
    constants,
    ChangeEmail,
    create_account,
    UserRegisterData,
)

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "CreateSerializer",
    "ChangePasswordSerializer",
    "ProfileSerializer",
    "CreateChangeEmailSerializer",
    "VerifyChangeEmailSerializer",
)


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
            User.username_validator,
            UniqueValidator(
                User.objects.all(),
                message=_("Already used.")
            )
        ],
        max_length=constants.USER_USERNAME_MAX_LENGTH)
    name = serializers.CharField(
        max_length=constants.USER_NAME_MAX_LENGTH)
    # client_id = serializers.CharField()

    def validate_state(self, value: str):
        enrollment = self.context['enrollment']  # type: Enrollment
        if not enrollment.check_state(value):
            self.fail("invalid_param")
        return None

    def validate_otp_id(self, value: str):
        enrollment = self.context['enrollment']  # type: Enrollment
        if not constant_time_compare(
                enrollment.otp_token.subid, value):
            self.fail("invalid_param")

    def validate_otp_token(self, value: str):
        enrollment = self.context['enrollment']  # type: Enrollment
        if not constant_time_compare(
                enrollment.otp_token.token, value):
            self.fail("invalid_param")

    def update(self, instance: Enrollment, validated_data: dict) -> User:
        raise Exception(instance, validated_data)

    def create(self, validated_data) -> User:
        validated_data.pop("state")
        validated_data.pop("otp_id")
        validated_data.pop("otp_token")
        # enrollment = self.context["enrollment"]  # type: Enrollment
        validated_data["enrollment"] = self.context["enrollment"]
        return create_account(UserRegisterData(**validated_data))
        # if enrollment.email_id:
        #     validated_data["email"] = enrollment.email.address
        # if enrollment.phone_id:
        #     validated_data["phone"] = enrollment.phone.number
        # return User.objects.create_user(**validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    default_error_messages = {
        "invalid_format": _("Invalid format."),
        "invalid_password": _("Invalid password."),
        "same_password": _("Must be different from the old password.")
    }

    old_password = Base64Field(
        strict=False, urlsafe=True)
    new_password = Base64Field(
        strict=False, urlsafe=True)

    def _decrypt(self, value: bytes) -> bytes:
        request = self.context["request"]
        try:
            return request.platform.decrypt(
                value, struct.pack(b'>Q', request.timestamp)
            )
        except ValueError:
            self.fail("invalid_format")

    def validate_old_password(self, value: bytes) -> str:
        return self._decrypt(value).decode()

    def validate_new_password(self, value: bytes) -> str:
        value = self._decrypt(value)
        validate_password(value)
        return value.decode()

    def validate(self, attrs: dict) -> dict:
        old_password = attrs.pop("old_password")
        if not self.instance.check_password(old_password):
            raise serializers.ValidationError({
                "old_password": self.error_messages["invalid_password"]
            }, "invalid_password")
        if constant_time_compare(old_password, attrs["new_password"]):
            raise serializers.ValidationError({
                "new_password": self.error_messages["same_password"]
            }, "same_password")
        return attrs

    def update(self, instance: User, validated_data: dict) -> User:
        instance.update_password(
            validated_data["new_password"])
        return instance


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            "name",
        )
        extra_kwargs = {
            "name": {"required": True}
        }


class CreateChangeEmailSerializer(serializers.Serializer):
    default_error_messages = {
        "current_email": _("This email is your current email."),
        "registered": _("Please use another email.")
    }

    email = serializers.EmailField(
        write_only=True)
    state = serializers.CharField(
        write_only=True,
        max_length=constants.CHANGE_EMAIL_STATE_LENGTH)

    ref_id = serializers.ReadOnlyField(
        source="user.subid")
    id = serializers.ReadOnlyField(
        source="subid")

    class Meta:
        model = ChangeEmail
        fields = (
            "email",
        )

    def validate_email(self, value: str) -> str:
        user = self.context["request"].user  # type: User
        if value == user.email:
            self.fail("current_email")
        if User.objects.filter(email=value).exists():
            self.fail("registered")
        return value

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["device_id"] = request.COOKIES["device_id"]
        validated_data["user_agent"] = request.headers["User-Agent"]
        validated_data["user"] = request.user
        return ChangeEmail.objects.create(**validated_data)


class VerifyChangeEmailSerializer(serializers.Serializer):
    instance: "ChangeEmail"
    default_error_messages = {
        "invalid_param": _("Invalid."),
        "invalid_format": _("Invalid format."),
    }

    state = serializers.CharField()
    otp_id = serializers.CharField()
    otp_token = serializers.CharField()
    password = Base64Field(
        strict=False, urlsafe=True)

    def validate_state(self, value: str):
        instance = self.instance
        if not instance.check_state(value):
            self.fail("invalid_param")
        return None

    def validate_otp_id(self, value: str):
        instance = self.instance
        if not constant_time_compare(
                instance.otp_token.subid, value):
            self.fail("invalid_param")

    def validate_otp_token(self, value: str):
        instance = self.instance
        if not constant_time_compare(
                instance.otp_token.token, value):
            self.fail("invalid_param")

    def validate_password(self, value: bytes) -> None:
        request = self.context["request"]
        try:
            password = request.platform.decrypt(
                value, struct.pack(b'>Q', request.timestamp)
            )
        except ValueError:
            self.fail("invalid_format")
        else:
            if not request.user.check_password(password):
                self.fail("invalid_param")

    def update(self, instance: ChangeEmail, validated_data: dict):
        instance.apply()
        return instance
