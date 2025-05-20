from __future__ import annotations
from typing import TYPE_CHECKING, Any

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import gettext_lazy as _

from evercore_jwt_auth.settings import jwt_auth_settings

from ..rbac import RoleUser
from ..refresh_token.plugin_base import RefreshTokenPluginBase

if TYPE_CHECKING:
    from authn.models import TenantUser


logger = logging.getLogger(__name__)
__all__ = (
    "RTPluginTenantQuerySet",
    "RTPluginTenantManager",
    "RTPluginTenant",
)


class RTPluginTenantQuerySet(models.QuerySet):
    pass


_RTPluginTenantManagerBase = models.Manager.from_queryset(
    RTPluginTenantQuerySet
)  # type: type[RTPluginTenantQuerySet]


class RTPluginTenantManager(_RTPluginTenantManagerBase, BaseManager):
    pass


class RTPluginTenant(RefreshTokenPluginBase):
    tenant_user_id: int
    tenant_user = models.ForeignKey(
        "authn.TenantUser", on_delete=models.CASCADE,
        verbose_name=_("tenant user")
    )  # type: TenantUser

    objects = RTPluginTenantManager()

    def get_extra_claims(self) -> dict[str, Any]:
        tenant_user = self.tenant_user
        return {
            jwt_auth_settings.TENANT_ID_CLAIM: tenant_user.tenant_id,
            jwt_auth_settings.TENANT_OWNER_CLAIM: tenant_user.is_owner,
            jwt_auth_settings.RBAC_ROLE_IDS_CLAIM: tuple(
                RoleUser.objects.filter(
                    tenant_id=tenant_user.tenant_id,
                    user_id=tenant_user.user_id
                ).values_list(
                    "role_id", flat=True
                )
            )
        }
