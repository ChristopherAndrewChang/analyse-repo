from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import gettext_lazy as _

from . import constants

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "IssuerQuerySet",
    "IssuerManager",
    "Issuer",
)


class IssuerQuerySet(models.QuerySet):
    pass


_IssuerManagerBase = models.Manager.from_queryset(
    IssuerQuerySet
)  # type: type[IssuerQuerySet]


class IssuerManager(_IssuerManagerBase, BaseManager):
    pass


class Issuer(models.Model):
    name = models.CharField(
        _("name"), max_length=constants.ISSUER_NAME_LENGTH,
        unique=True)

    objects = IssuerManager()
