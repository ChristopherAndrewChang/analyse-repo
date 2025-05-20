from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField

from idvalid_core.models import get_subid_model

if TYPE_CHECKING:
    from datetime import datetime
    from phonenumber_field.phonenumber import PhoneNumber


logger = logging.getLogger(__name__)
__all__ = (
    "PhoneQuerySet",
    "PhoneManager",
    "Phone",
)


class PhoneQuerySet(models.QuerySet):
    pass


_PhoneManagerBase = models.Manager.from_queryset(
    PhoneQuerySet
)  # type: type[PhoneQuerySet]


class PhoneManager(_PhoneManagerBase, BaseManager):
    pass


class Phone(get_subid_model()):
    number = PhoneNumberField(
        _("phone"), unique=True)  # type: PhoneNumber | None

    resend_date = models.DateTimeField(
        _("resend date"), null=True, blank=True,
        editable=False)  # type: datetime

    is_registered = models.BooleanField(
        _("registered flag"), default=False, editable=False)
    registered_date = models.DateTimeField(
        _("registered"), null=True, blank=True, editable=False)

    created = models.DateTimeField(
        _("created"), auto_now_add=True, editable=False)

    objects = PhoneManager()

    def allow_resend(self) -> bool:
        if self.resend_date is None:
            return True
        return timezone.now() >= self.resend_date

    def update_resend_date(self, value: datetime, *, save: bool = True):
        self.resend_date = value
        if save:
            self.save(update_fields=['resend_date'])

    def register(self, *, save: bool = True):
        if self.is_registered:
            raise TypeError("already registered")
        self.is_registered = True
        self.registered_date = timezone.now()
        if save:
            self.save(update_fields=["is_registered", "registered_date"])
