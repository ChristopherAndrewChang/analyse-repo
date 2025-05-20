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
    "EnrollmentQuerySet",
    "EnrollmentManager",
    "Enrollment",
)


class EnrollmentQuerySet(models.QuerySet):
    def create(self, *, email: str, include_otp: bool = False, otp_kwargs: dict = None) -> Enrollment:
        obj = self.model(email=email)  # type: Enrollment
        obj._generate_otp = include_otp
        obj._otp_kwargs = otp_kwargs
        self._for_write = True
        obj.save(force_insert=True, using=self.db)
        return obj


_EnrollmentManagerBase = models.Manager.from_queryset(
    EnrollmentQuerySet
)  # type: type[EnrollmentQuerySet]


class EnrollmentManager(_EnrollmentManagerBase):
    pass


class Enrollment(get_subid_model()):
    # temp variable to recognize otp creation on create
    # handled in pre_save receiver
    _generate_otp: bool
    _otp_kwargs: dict
    # temp variable to store grpc response
    otp_response: "CreateResponse"

    otp_set: "OtpManager"

    email = models.EmailField(
        _("email"), unique=True)  # type: str

    last_otp_id = models.CharField(
        _("last otp id"), max_length=OTP_ID_LENGTH, unique=True,
        null=True, blank=True, editable=False)
    last_otp_sent = models.DateTimeField(
        _("last otp sent date"), null=True, blank=True,
        editable=False)  # type: datetime

    is_registered = models.BooleanField(
        _("registered flag"), default=False, editable=False)
    registered_date = models.DateTimeField(
        _("registered"), null=True, blank=True, editable=False)

    created = models.DateTimeField(
        _("created"), auto_now_add=True, editable=False)

    objects = EnrollmentManager()

    def resend_date(self) -> datetime:
        return self.last_otp_sent + timedelta(
            seconds=enrollment_settings.OTP_RESEND)

    def allow_resend(self) -> bool:
        return timezone.now() >= self.resend_date()

    def refresh_otp(self, *, save: bool = True, **kwargs) -> CreateResponse:
        response = generate_otp(self, **kwargs)
        self.last_otp_id = response.id
        self.last_otp_sent = timezone.now()
        if save:
            self.save(update_fields=["last_otp_id", "last_otp_sent"])
        return response

    def register(self, *, save: bool = True):
        if self.is_registered:
            raise TypeError("already registered")
        self.is_registered = True
        self.registered_date = timezone.now()
        if save:
            self.save(update_fields=["is_registered", "registered_date"])


@receiver(pre_save, sender=Enrollment)
def on_enrollment_pre_save(instance: Enrollment, **kwargs):
    if getattr(instance, "_generate_otp", False):
        instance.otp_response = instance.refresh_otp(
            save=False, **getattr(instance, "_otp_kwargs", {}))
