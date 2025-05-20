from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from datetime import timedelta

from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.db.models.manager import BaseManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from idvalid_core.models import get_subid_model

from enrollment.generator import generate_otp_expires, generate_otp_resend
from enrollment.settings import enrollment_settings
from enrollment.signals import code_applied

from . import constants

if TYPE_CHECKING:
    from idvalid_integration.protos.models import otp_pb2
    from .email import Email


logger = logging.getLogger(__name__)
__all__ = (
    "CodeQuerySet",
    "CodeManager",
    "Code",
)


class CodeQuerySet(models.QuerySet):
    def create(self, email: Email | str, state: str, **kwargs) -> Code:
        if 'expires' not in kwargs:
            kwargs['expires'] = generate_otp_expires()

        if isinstance(email, str):
            from .email import Email
            email, created = Email.objects.get_or_create(
                email=email,
                defaults={
                    "resend_date": generate_otp_resend()
                })
            if not created:
                email.update_resend_date(generate_otp_resend())
        else:
            email.update_resend_date(generate_otp_resend())

        return super().create(
            email=email, state=make_password(state), **kwargs)


_CodeManagerBase = models.Manager.from_queryset(
    CodeQuerySet
)  # type: type[CodeQuerySet]


class CodeManager(_CodeManagerBase, BaseManager):
    pass


class Code(get_subid_model()):
    _raw_state: str

    email = models.ForeignKey(
        "enrollment.Email", on_delete=models.CASCADE,
        related_name="code_set",
        verbose_name=_("email"))  # type: Email

    # security
    device_id = models.CharField(
        _("device id"), max_length=constants.DEVICE_ID_LENGTH)
    state = models.CharField(
        _("state"), max_length=128)
    user_agent = models.CharField(
        _("user agent"), max_length=512)

    expires = models.DateTimeField(
        _("expired date"))

    otp_id = models.TextField(
        _("otp id"), null=True, blank=True)
    otp_token = models.TextField(
        _("otp token"), null=True, blank=True)

    # internal flags
    # is_confirmed = models.BooleanField(
    #     _("confirmed flag"), default=False, editable=False)
    # confirmed_date = models.DateTimeField(
    #     _("confirmed date"), null=True, blank=True, editable=False)

    # logs
    created = models.DateTimeField(
        _("created"), auto_now_add=True, editable=False)

    objects = CodeManager()

    def set_state(self, raw_value: str):
        self.state = make_password(raw_value)
        self._raw_state = raw_value

    def check_state(self, raw_value: str) -> bool:
        def upgrade(value: str):
            self.set_state(value)
            self._raw_state = None
            self.save(update_fields=["state"])
        return check_password(raw_value, self.state, upgrade)

    def apply(
            self, message: otp_pb2.Otp, *,
            save: bool = True, using: str = None):
        self.otp_id = message.id
        self.otp_token = message.token
        if save:
            self.save(
                update_fields=["otp_id", "otp_token"],
                using=using)
            code_applied.send(
                sender=self.__class__, instance=self, using=self._state.db)
