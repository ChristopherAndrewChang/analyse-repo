from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "HistoryQuerySet",
    "HistoryManager",
    "History",
)


class HistoryQuerySet(models.QuerySet):
    pass


_HistoryManagerBase = models.Manager.from_queryset(
    HistoryQuerySet
)  # type: type[HistoryQuerySet]


class HistoryManager(_HistoryManagerBase, BaseManager):
    pass


class History(models.Model):
    code = models.ForeignKey(
        "otp.Code", on_delete=models.CASCADE,
        verbose_name=_("code"))
    tag = models.CharField(
        _("tag"), max_length=128)
    description = models.TextField(
        _("description"))
    created = models.DateTimeField(
        _("created"), auto_now_add=True)
