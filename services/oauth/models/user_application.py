from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import gettext_lazy as _

from idvalid_core.models import get_subid_model

if TYPE_CHECKING:
    from .user import User
    from .application import Application


logger = logging.getLogger(__name__)
__all__ = (
    "UserApplicationQuerySet",
    "UserApplicationManager",
    "UserApplication",
)


class UserApplicationQuerySet(models.QuerySet):
    pass


_UserApplicationManagerBase = models.Manager.from_queryset(
    UserApplicationQuerySet
)  # type: type[UserApplicationQuerySet]


class UserApplicationManager(_UserApplicationManagerBase, BaseManager):
    pass


class UserApplication(get_subid_model()):
    user_id = models.PositiveBigIntegerField(
        _("user id"))

    application_id: int
    application = models.ForeignKey(
        "oauth.Application", on_delete=models.CASCADE,
        related_name="allowed_users",
        verbose_name=_("application"))  # type: Application

    created = models.DateTimeField(
        _("created time"), auto_now_add=True)
    last_accessed = models.DateTimeField(
        _("last accessed"), null=True, blank=True)

    objects = UserApplicationManager()

    class Meta:
        unique_together = ("user_id", "application")
