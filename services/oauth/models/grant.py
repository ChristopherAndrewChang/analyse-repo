from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import gettext_lazy as _

from oauth2_provider.models import AbstractGrant

from .base import TemporaryUser

if TYPE_CHECKING:
    from .application import Application


logger = logging.getLogger(__name__)
__all__ = (
    "GrantQuerySet",
    "GrantManager",
    "Grant",
)


class GrantQuerySet(models.QuerySet):
    pass


_GrantManagerBase = models.Manager.from_queryset(
    GrantQuerySet
)  # type: type[GrantQuerySet]


class GrantManager(_GrantManagerBase, BaseManager):
    pass


class Grant(TemporaryUser, AbstractGrant):
    application_id: int
    application: Application

    user_id = models.PositiveBigIntegerField(
        _("user id"))

    objects = GrantManager()
