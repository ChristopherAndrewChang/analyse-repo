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
    "RecipientTypeQuerySet",
    "RecipientTypeManager",
    "RecipientType",
)


class RecipientTypeQuerySet(models.QuerySet):
    pass


_RecipientTypeManagerBase = models.Manager.from_queryset(
    RecipientTypeQuerySet
)  # type: type[RecipientTypeQuerySet]


class RecipientTypeManager(_RecipientTypeManagerBase, BaseManager):
    pass


class RecipientType(models.Model):
    name = models.CharField(
        _("name"), max_length=constants.RECIPIENT_TYPE_NAME_LENGTH, unique=True)

    objects = RecipientTypeManager()
