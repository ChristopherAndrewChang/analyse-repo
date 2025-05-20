from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from datetime import timedelta

from django.db import models
from django.dispatch.dispatcher import receiver
from django.db.models.signals import pre_save
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from idvalid_core.models import get_subid_model

from enrollment.integration.rpc import generate_otp
from enrollment.settings import enrollment_settings

from .constants import OTP_ID_LENGTH

if TYPE_CHECKING:
    from datetime import datetime
    from idvalid_integration.rpc.otp.code import CreateResponse
    from .otp import OtpManager


logger = logging.getLogger(__name__)
__all__ = (
    "EmailQuerySet",
    "EmailManager",
    "Email",
)


class EmailQuerySet(models.QuerySet):
    pass


_EmailManagerBase = models.Manager.from_queryset(
    EmailQuerySet
)  # type: type[EmailQuerySet]


class EmailManager(_EmailManagerBase):
    pass


class Email(get_subid_model()):
    email = models.EmailField(
        _("email"), unique=True)  # type: str

    resend_date = models.DateTimeField(
        _("resend_date"), null=True, blank=True,
        editable=False)  # type: datetime

    is_registered = models.BooleanField(
        _("registered flag"), default=False, editable=False)
    registered_date = models.DateTimeField(
        _("registered"), null=True, blank=True, editable=False)

    created = models.DateTimeField(
        _("created"), auto_now_add=True, editable=False)

    objects = EmailManager()

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
