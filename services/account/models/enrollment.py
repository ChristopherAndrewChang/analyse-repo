from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.db.models.manager import BaseManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from idvalid_core.models import get_subid_model

from account.generators import generate_otp_expires, generate_otp_resend

from . import constants
from .email import Email
from .otp_token import OtpToken

if TYPE_CHECKING:
    # from idvalid_integration.protos.models.enrollment_pb2 import (
    #     Enrollment as EnrollmentMessage)
    from typing import Self


logger = logging.getLogger(__name__)
__all__ = (
    "EnrollmentQuerySet",
    "EnrollmentManager",
    "Enrollment",
)


class EnrollmentQuerySet(models.QuerySet):
    def create(self, email: Email | str, state: str, **kwargs) -> Enrollment:
        if isinstance(email, str):
            email, created = Email.objects.get_or_create(
                address=email,
                defaults={
                    "resend_date": generate_otp_resend()
                })
            if not created:
                email.update_resend_date(generate_otp_resend())
        else:
            email.update_resend_date(generate_otp_resend())

        return super().create(
            email=email, state=make_password(state), **kwargs)

    def suppress(self, email: Email) -> int:
        return self.filter(
            suppressed=False,
            email=email,
        ).update(
            suppressed=True,
            suppressed_time=timezone.now()
        )

    def active(self) -> Self:
        return self.filter(
            suppressed=False,
            email__is_registered=False,
            otp_token_id__isnull=False)


_EnrollmentManagerBase = models.Manager.from_queryset(
    EnrollmentQuerySet
)  # type: type[EnrollmentQuerySet]


class EnrollmentManager(_EnrollmentManagerBase, BaseManager):
    pass


class Enrollment(get_subid_model()):
    _raw_state: str

    email_id: int
    email = models.ForeignKey(
        "account.Email", on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name=_("email"))  # type: Email

    # security
    device_id = models.CharField(
        _("device id"), max_length=constants.DEVICE_ID_LENGTH)
    state = models.CharField(
        _("state"), max_length=128)
    user_agent = models.TextField(
        _("user agent"))

    expires = models.DateTimeField(
        _("expired date"), default=generate_otp_expires)

    otp_token_id: int
    otp_token = models.OneToOneField(
        "account.OtpToken", on_delete=models.CASCADE,
        verbose_name=_("otp token"),
        null=True, blank=True)  # type: OtpToken

    suppressed = models.BooleanField(
        _("suppressed flag"), default=False)
    suppressed_time = models.DateTimeField(
        _("suppressed time"), null=True, blank=True)

    # logs
    created = models.DateTimeField(
        _("created"), auto_now_add=True, editable=False)

    objects = EnrollmentManager()

    def set_state(self, raw_value: str):
        self.state = make_password(raw_value)
        self._raw_state = raw_value

    def check_state(self, raw_value: str) -> bool:
        def upgrade(value: str):
            self.set_state(value)
            self._raw_state = None
            self.save(update_fields=["state"])

        return check_password(raw_value, self.state, upgrade)

    def setup_token(
            self, otp_id: str, token: str, *,
            using: str = None):
        if self.otp_token_id:
            raise TypeError("Already has token")

        otp_token = OtpToken.objects.create(
            subid=otp_id,
            token=token)
        self.otp_token = otp_token
        self.save(
            update_fields=["otp_token"],
            using=using)

    # def apply(
    #         self, message: otp_pb2.Otp, *,
    #         save: bool = True, using: str = None):
    #     self.otp_id = message.id
    #     self.otp_token = message.token
    #     if save:
    #         self.save(
    #             update_fields=["otp_id", "otp_token"],
    #             using=using)
    #         code_applied.send(
    #             sender=self.__class__, instance=self, using=self._state.db)
