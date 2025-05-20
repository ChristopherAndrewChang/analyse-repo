from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import gettext_lazy as _

from oauth2_provider.models import AbstractIDToken

from .base import TemporaryUser

if TYPE_CHECKING:
    from .application import Application


logger = logging.getLogger(__name__)
__all__ = (
    "IDTokenQuerySet",
    "IDTokenManager",
    "IDToken",
)


class IDTokenQuerySet(models.QuerySet):
    pass


_IDTokenManagerBase = models.Manager.from_queryset(
    IDTokenQuerySet
)  # type: type[IDTokenQuerySet]


class IDTokenManager(_IDTokenManagerBase, BaseManager):
    pass


class IDToken(TemporaryUser, AbstractIDToken):
    application_id: int | None
    application: Application | None

    user_id = models.PositiveBigIntegerField(
        _("user id"))

    objects = IDTokenManager()
