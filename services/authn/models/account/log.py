from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    import datetime
    from authn.models import User


logger = logging.getLogger(__name__)
__all__ = (
    "UserLogQuerySet",
    "UserLogManager",
    "UserLog",
)


class UserLogQuerySet(models.QuerySet):
    pass


_UserLogManagerBase = models.Manager.from_queryset(
    UserLogQuerySet
)  # type: type[UserLogQuerySet]


class UserLogManager(_UserLogManagerBase, BaseManager):
    pass


class UserLog(models.Model):
    user_id: int
    user = models.OneToOneField(
        "authn.User", on_delete=models.CASCADE,
        primary_key=True,
        related_name="log",
        verbose_name=_("user"),
    )  # type: User

    date_joined = models.DateTimeField(
        _("date joined"), default=timezone.now)
    last_login = models.DateTimeField(
        _("last login"), blank=True, null=True)
    admin_last_login = models.DateTimeField(
        _("admin last login"), blank=True, null=True)

    objects = UserLogManager()

    def update_last_login(self, *, current_time: datetime.datetime = None, save: bool = True):
        if current_time is None:
            current_time = timezone.now()

        self.last_login = current_time
        if save:
            self.save(update_fields=["last_login"])

        return current_time
