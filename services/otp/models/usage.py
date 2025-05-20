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
    "UsageQuerySet",
    "UsageManager",
    "Usage",
)


class UsageQuerySet(models.QuerySet):
    pass


_UsageManagerBase = models.Manager.from_queryset(
    UsageQuerySet
)  # type: type[UsageQuerySet]


class UsageManager(_UsageManagerBase, BaseManager):
    pass


class Usage(models.Model):
    name = models.CharField(
        _("name"), max_length=constants.USAGE_NAME_LENGTH,
        unique=True)

    objects = UsageManager()
