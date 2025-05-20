from __future__ import annotations

import builtins
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from .recipient_type import RecipientType


logger = logging.getLogger(__name__)
__all__ = (
    "RecipientQuerySet",
    "RecipientManager",
    "Recipient",
)


class RecipientQuerySet(models.QuerySet):
    def create(self, *, type: str | RecipientType, **kwargs) -> Recipient:
        if isinstance(type, str):
            from .recipient_type import RecipientType
            type = RecipientType.objects.get(name=type)
        return super().create(type=type, **kwargs)


_RecipientManagerBase = models.Manager.from_queryset(
    RecipientQuerySet
)  # type: type[RecipientQuerySet]


class RecipientManager(_RecipientManagerBase, BaseManager):
    pass


class Recipient(models.Model):
    CONTACT_LENGTH = 128

    type = models.ForeignKey(
        "otp.RecipientType", on_delete=models.CASCADE,
        verbose_name=_("type"))  # type: RecipientType
    contact = models.CharField(
        _("contact"), max_length=CONTACT_LENGTH)

    objects = RecipientManager()

    class Meta:
        unique_together = ("type", "contact")
