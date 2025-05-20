from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from account.generators import generate_otp_token_expires

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "OtpTokenQuerySet",
    "OtpTokenManager",
    "OtpToken",
)


class OtpTokenQuerySet(models.QuerySet):
    pass


_OtpTokenManagerBase = models.Manager.from_queryset(
    OtpTokenQuerySet
)  # type: type[OtpTokenQuerySet]


class OtpTokenManager(_OtpTokenManagerBase, BaseManager):
    pass


class OtpToken(models.Model):
    subid = models.TextField(
        _("subid"))
    token = models.TextField(
        _("token"))
    expires = models.DateTimeField(
        _("expires"), default=generate_otp_token_expires)

    applied = models.BooleanField(
        _("applied flag"), default=False)
    applied_time = models.DateTimeField(
        _("applied time"), null=True, blank=True)

    created = models.DateTimeField(
        _("created time"), auto_now_add=True)

    objects = OtpTokenManager()

    def is_expired(self) -> bool:
        return timezone.now() >= self.expires
