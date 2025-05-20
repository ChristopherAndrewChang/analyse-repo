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

from authn.settings import authn_settings

from . import constants
from .otp_token import OtpToken

if TYPE_CHECKING:
    import datetime
    from typing import Self
    from authn.models import User


logger = logging.getLogger(__name__)
__all__ = (
    "ForgetPasswordQuerySet",
    "ForgetPasswordManager",
    "ForgetPassword",

    "ForgetPasswordStateQuerySet",
    "ForgetPasswordStateManager",
    "ForgetPasswordState",
)


def default_otp_expires() -> datetime.datetime:
    duration = authn_settings.FORGET_PASSWORD_OTP_DURATION
    return timezone.now() + timedelta(seconds=duration)


def default_otp_resend() -> datetime.datetime:
    duration = authn_settings.FORGET_PASSWORD_OTP_RESEND
    return timezone.now() + timedelta(seconds=duration)


class ForgetPasswordQuerySet(models.QuerySet):
    def create(self, state: str, **kwargs) -> ForgetPassword:
        return super().create(
            state=make_password(state), **kwargs)

    def suppress(self, user: User) -> int:
        return self.filter(
            suppressed=False,
            user=user,
        ).update(
            suppressed=True,
            suppressed_time=timezone.now()
        )

    def active(self) -> Self:
        return self.filter(
            suppressed=False,
            otp_token_id__isnull=False,
            otp_token__applied=False)


_ForgetPasswordManagerBase = models.Manager.from_queryset(
    ForgetPasswordQuerySet
)  # type: type[ForgetPasswordQuerySet]


class ForgetPasswordManager(_ForgetPasswordManagerBase, BaseManager):
    pass


class ForgetPassword(get_subid_model()):
    _raw_state: str

    user_id: int
    user = models.ForeignKey(
        "authn.User", on_delete=models.CASCADE,
        related_name="forget_passwords",
        verbose_name=_("user"))  # type: User

    # security
    device_id = models.CharField(
        _("device id"), max_length=constants.DEVICE_ID_LENGTH)
    state = models.CharField(
        _("state"), max_length=128)
    user_agent = models.TextField(
        _("user agent"))

    expires = models.DateTimeField(
        _("expired date"), default=default_otp_expires)

    otp_token_id: int
    otp_token = models.OneToOneField(
        "authn.OtpToken", on_delete=models.CASCADE,
        verbose_name=_("otp token"),
        null=True, blank=True)  # type: OtpToken

    suppressed = models.BooleanField(
        _("suppressed flag"), default=False)
    suppressed_time = models.DateTimeField(
        _("suppressed time"), null=True, blank=True)

    # logs
    created = models.DateTimeField(
        _("created"), auto_now_add=True, editable=False)

    objects = ForgetPasswordManager()

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


class ForgetPasswordStateQuerySet(models.QuerySet):
    pass


_ForgetPasswordStateManagerBase = models.Manager.from_queryset(
    ForgetPasswordStateQuerySet
)  # type: type[ForgetPasswordStateQuerySet]


class ForgetPasswordStateManager(
        _ForgetPasswordStateManagerBase, BaseManager):
    pass


class ForgetPasswordState(models.Model):
    user_id: int
    user = models.OneToOneField(
        "authn.User", on_delete=models.CASCADE,
        related_name="fp_state",
        verbose_name=_("user"))  # type: User

    resend_date = models.DateTimeField(
        _("resend_date"),
        default=default_otp_resend,
        editable=False,
        null=True,
        blank=True
    )  # type: datetime.datetime

    objects = ForgetPasswordStateManager()

    def allow_resend(self) -> bool:
        if self.resend_date is None:
            return True
        return timezone.now() >= self.resend_date

    def set_resend_date(
            self, value: datetime.datetime | None, *,
            save: bool = True):
        self.resend_date = value
        if save:
            self.save(update_fields=["resend_date"])

    def renew_resend_date(self, *, save: bool = True):
        self.set_resend_date(
            default_otp_resend(), save=save)

    def clear_resend_date(self, *, save: bool = True):
        self.set_resend_date(
            None, save=save)
