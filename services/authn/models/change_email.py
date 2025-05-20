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
    "ChangeEmailQuerySet",
    "ChangeEmailManager",
    "ChangeEmail",
)


def default_otp_expires() -> datetime.datetime:
    duration = authn_settings.CHANGE_EMAIL_OTP_DURATION
    return timezone.now() + timedelta(seconds=duration)


class ChangeEmailQuerySet(models.QuerySet):
    def create(self, state: str, **kwargs) -> ChangeEmail:
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


_ChangeEmailManagerBase = models.Manager.from_queryset(
    ChangeEmailQuerySet
)  # type: type[ChangeEmailQuerySet]


class ChangeEmailManager(_ChangeEmailManagerBase, BaseManager):
    pass


class ChangeEmail(get_subid_model()):
    _raw_state: str

    user_id: int
    user = models.ForeignKey(
        "authn.User", on_delete=models.CASCADE,
        related_name="change_emails",
        verbose_name=_("user"))  # type: User

    email = models.EmailField(
        _("email"))

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

    objects = ChangeEmailManager()

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

    def apply(self):
        user = self.user
        user.email = self.email
        user.save(update_fields=["email"])
        self.otp_token.apply()
