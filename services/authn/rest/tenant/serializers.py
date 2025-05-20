from __future__ import annotations
from typing import TYPE_CHECKING

import logging
import struct

from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from evercore.rest import Base64Field

from authn.models import TenantUser, RTPluginTenant
from authn.tokens import AccessToken

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "TenantSerializer",
)


class TenantSerializer(serializers.Serializer):
    default_error_messages = {
        "invalid_format": _("Invalid format."),
        "invalid_tenant": _("Invalid tenant.")
    }
    tenant = Base64Field(
        source="tenant_user", strict=False, urlsafe=True)

    def validate_tenant(self, value: bytes) -> TenantUser:
        request = self.context["request"]
        try:
            val = request.platform.decrypt(
                value, struct.pack(b'>Q', request.timestamp))
        except ValueError:
            self.fail("invalid_format")
        try:
            return TenantUser.objects.get(
                is_registered=True,
                is_active=True,
                tenant__subid=val.decode(),
                user_id=request.user.id)
        except TenantUser.DoesNotExist:
            self.fail("invalid_tenant")

    def validate(self, attrs):
        token = self.context["request"].auth  # type: AccessToken
        refresh = token.get_refresh_token_instance()
        refresh.set_plugin(
            RTPluginTenant.refresh_token.field.related_query_name(),
            **attrs
        )
        return {
            "access_token": str(
                refresh.get_access_jwt(current_time=token.current_time)
            ),
        }
