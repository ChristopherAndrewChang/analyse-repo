from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import gettext_lazy as _

from authn_sdk.constants import PROFILE_NAME_MAX_LENGTH

if TYPE_CHECKING:
    from authn.models import User


logger = logging.getLogger(__name__)
__all__ = (
    "UserProfileQuerySet",
    "UserProfileManager",
    "UserProfile",
)


class UserProfileQuerySet(models.QuerySet):
    pass


_UserProfileManagerBase = models.Manager.from_queryset(
    UserProfileQuerySet
)  # type: type[UserProfileQuerySet]


class UserProfileManager(_UserProfileManagerBase, BaseManager):
    pass


class UserProfile(models.Model):
    user_id: int
    user = models.OneToOneField(
        "authn.User", on_delete=models.CASCADE,
        primary_key=True,
        related_name="profile",
        verbose_name=_("user"),
    )  # type: User

    name = models.CharField(
        _("name"),
        max_length=PROFILE_NAME_MAX_LENGTH, null=True, blank=True)

    objects = UserProfileManager()
