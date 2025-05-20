from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import gettext_lazy as _

from oauth2_provider.models import AbstractAccessToken

from .base import TemporaryUser

if TYPE_CHECKING:
    from .refresh_token import RefreshToken
    from .id_token import IDToken
    from .application import Application


logger = logging.getLogger(__name__)
__all__ = (
    "AccessTokenQuerySet",
    "AccessTokenManager",
    "AccessToken",
)


class AccessTokenQuerySet(models.QuerySet):
    pass


_AccessTokenManagerBase = models.Manager.from_queryset(
    AccessTokenQuerySet
)  # type: type[AccessTokenQuerySet]


class AccessTokenManager(_AccessTokenManagerBase, BaseManager):
    pass


class AccessToken(TemporaryUser, AbstractAccessToken):
    source_refresh_token_id: int | None
    source_refresh_token: RefreshToken | None
    id_token_id: int | None
    id_token: IDToken | None
    application_id: int | None
    application: Application | None

    user_id = models.PositiveBigIntegerField(
        _("user id"), null=True, blank=True
    )

    objects = AccessTokenManager()
