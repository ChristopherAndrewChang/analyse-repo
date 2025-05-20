from __future__ import annotations
from typing import TYPE_CHECKING

import logging

# from django.utils.translation import gettext_lazy as _

from evercore_grpc.framework import serializers
# from evercore_grpc.framework.relations import SlugRelatedField

from idvalid_integration.rpc.authn.user import CreateResponse

from authn.models import (
    # Application,
    User,
)

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = ("CreateSerializer",)


class CreateSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="subid")

    # client_id = SlugRelatedField(
    #     slug_field="client_id",
    #     queryset=Application.objects.active(),
    #     write_only=True)

    class Meta:
        model = User
        read_proto_class = CreateResponse
        fields = (
            "id",
            "email",
            "username",
            "password",
            "name",
            "account_id",
            # "client_id",
        )
        extra_kwargs = {
            "email": {"write_only": True},
            "username": {"write_only": True},
            "name": {"write_only": True},
            "account_id": {"write_only": True},
        }

    def create(self, validated_data):
        # raise Exception(validated_data)
        # application = validated_data.pop("client_id")  # type: Application
        instance = User.objects.create_user(
            **validated_data)  # type: User
        # instance.allowed_applications.create(application=application)
        return instance
