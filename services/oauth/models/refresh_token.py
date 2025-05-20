from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import gettext_lazy as _

from oauth2_provider.models import AbstractRefreshToken

from .base import TemporaryUser

if TYPE_CHECKING:
    from .application import Application
    from .access_token import AccessToken


logger = logging.getLogger(__name__)
__all__ = (
    "RefreshTokenQuerySet",
    "RefreshTokenManager",
    "RefreshToken",
)


class RefreshTokenQuerySet(models.QuerySet):
    pass


_RefreshTokenManagerBase = models.Manager.from_queryset(
    RefreshTokenQuerySet
)  # type: type[RefreshTokenQuerySet]


class RefreshTokenManager(_RefreshTokenManagerBase, BaseManager):
    pass


class RefreshToken(TemporaryUser, AbstractRefreshToken):
    application_id: int
    application: Application
    access_token_id: int | None
    access_token: AccessToken | None

    user_id = models.PositiveBigIntegerField(
        _("user id"))

    objects = RefreshTokenManager()
