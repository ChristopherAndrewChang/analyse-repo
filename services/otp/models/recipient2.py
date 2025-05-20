from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import gettext_lazy as _

from idvalid_core.models import get_subid_model

# from . import constants

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "Recipient2QuerySet",
    "Recipient2Manager",
    "Recipient2",
)


class Recipient2QuerySet(models.QuerySet):
    pass


_Recipient2ManagerBase = models.Manager.from_queryset(
    Recipient2QuerySet
)  # type: type[Recipient2QuerySet]


class Recipient2Manager(_Recipient2ManagerBase, BaseManager):
    pass


class Recipient2(get_subid_model()):
    EMAIL_RECIPIENT_TYPE = 0
    PHONE_RECIPIENT_TYPE = 1
    USER_RECIPIENT_TYPE = 2
    RECIPIENT_TYPE_CHOICES = (
        (EMAIL_RECIPIENT_TYPE, "Email Address"),
        (PHONE_RECIPIENT_TYPE, "Phone Number"),
        (USER_RECIPIENT_TYPE, "User ID"),
    )

    recipient_type = models.PositiveSmallIntegerField(
        _("recipient type"), db_index=True, choices=RECIPIENT_TYPE_CHOICES)
    # can be email address, phone number, user id, or etc
    value = models.CharField(
        _("value"), max_length=128)

    objects = Recipient2Manager()

    class Meta:
        unique_together = ("recipient_type", "value")
