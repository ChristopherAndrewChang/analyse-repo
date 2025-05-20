from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import gettext_lazy as _

from idvalid_core.models import get_subid_model

from authn_sdk.constants import PROFILE_NAME_MAX_LENGTH

if TYPE_CHECKING:
    from typing import Self, Optional
    from idvalid_integration.protos.models import authn_pb2


logger = logging.getLogger(__name__)
__all__ = (
    "UserQuerySet",
    "UserManager",
    "User",
)


class UserQuerySet(models.QuerySet):
    def fetch_tenant_user(self, tenant_id: int) -> Self:
        return self.alias(
            _tenantuser_rel=models.FilteredRelation(
                "tenantuser",
                condition=models.Q(
                    tenantuser__tenant_id=tenant_id,
                )
            )
        )

    def fetch_role_user(self, role_id: int) -> Self:
        return self.alias(
            _roleuser_rel=models.FilteredRelation(
                "roleuser",
                condition=models.Q(
                    roleuser__role_id=role_id
                )
            )
        )

    def filter_tenant(self, tenant_id: int):
        return self.fetch_tenant_user(
            tenant_id
        ).filter(
            _tenantuser_rel__isnull=False
        )

    def filter_role(
            self, tenant_id: int, role_id: int, *,
            selected: Optional[bool] = None) -> Self:
        queryset = self.fetch_tenant_user(
            tenant_id
        ).fetch_role_user(
            role_id
        ).annotate(
            is_available=models.ExpressionWrapper(
                models.Q(_tenantuser_rel__isnull=False),
                output_field=models.BooleanField()
            ),
            selected=models.ExpressionWrapper(
                models.Q(_roleuser_rel__isnull=False),
                output_field=models.BooleanField()
            ),
            object_id=models.F("_roleuser_rel__subid")
        )
        if selected is None:
            return queryset.filter(
                models.Q(is_available=True) |
                models.Q(selected=True)
            )
        return queryset.filter(selected=selected)


_UserManagerBase = models.Manager.from_queryset(
    UserQuerySet
)  # type: type[UserQuerySet]


class UserManager(_UserManagerBase, BaseManager):
    def create_or_update_from_message(
            self, message: authn_pb2.Account) -> User:
        user_message = message.user
        try:
            instance = self.get(pk=user_message.id)  # type: User
        except self.model.DoesNotExist:
            instance = self.model(pk=user_message.id)  # type: User
        instance.subid = user_message.subid
        instance.is_active = user_message.is_active
        instance.name = message.profile.name
        instance.save()
        return instance

    def update_active_flag_from_message(
            self, message: authn_pb2.UserActiveFlag) -> int:
        return self.filter(
            pk=message.user_id
        ).update(
            is_active=message.is_active
        )

    def get_and_update_active_flag_from_message(
            self, message: authn_pb2.UserActiveFlag) -> User:
        """
        Get and update user `is_active` field.
        Raise DoesNotExist if user does not exist.
        :param message: authn_pb2.UserActiveFlag
        :return: User
        """
        instance = self.get(pk=message.user_id)  # type: User
        instance.update_active_flag(message.is_active)
        return instance

    def update_profile_from_message(
            self, message: authn_pb2.UserProfile) -> int:
        return self.filter(
            pk=message.user_id
        ).update(
            name=message.name
        )

    def get_and_update_profile_from_message(
            self, message: authn_pb2.UserProfile) -> User:
        """
        Get and update user `name` field.
        Raise DoesNotExist if user does not exist.
        :param message: authn_pb2.UserProfile
        :return: User
        """
        instance = self.get(pk=message.user_id)  # type: User
        instance.update_profile(message.name)
        return instance


class User(get_subid_model()):
    name = models.CharField(
        _("name"), max_length=PROFILE_NAME_MAX_LENGTH,
        null=True, blank=True
    )
    is_active = models.BooleanField(_("active flag"))

    objects = UserManager()

    def __str__(self):
        return f"{self.name} (ID: {self.pk})"

    def update_active_flag(
            self, value: bool, *,
            save: bool = True):
        self.is_active = value
        if save:
            self.save(update_fields=["is_active"])

    def update_profile(
            self, name: str, *,
            save: bool = True):
        self.name = name
        if save:
            self.save(update_fields=["name"])

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
