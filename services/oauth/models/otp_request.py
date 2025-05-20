from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from idvalid_core.models import get_subid_model

if TYPE_CHECKING:
    from .application import Application


logger = logging.getLogger(__name__)
__all__ = (
    "OtpRequestQuerySet",
    "OtpRequestManager",
    "OtpRequest",
)


class OtpRequestQuerySet(models.QuerySet):
    pass


_OtpRequestManagerBase = models.Manager.from_queryset(
    OtpRequestQuerySet
)  # type: type[OtpRequestQuerySet]


class OtpRequestManager(_OtpRequestManagerBase, BaseManager):
    pass


class OtpRequest(get_subid_model()):
    application_id: int
    application = models.ForeignKey(
        "oauth.Application", on_delete=models.CASCADE
    )  # type: Application
    user_id = models.PositiveBigIntegerField(
        _("user id"),
    )

    otp = models.CharField(
        _("otp"),
        max_length=6, null=True, blank=True)
    expires = models.DateTimeField(
        _("expires"),
        null=True, blank=True)

    objects = OtpRequestManager()

    def renew(self, *, save: bool = True):
        self.otp = None
        self.expires = None
        if save:
            self.save(update_fields=["otp", "expires"])

    def is_alive(self) -> bool:
        return self.expires >= timezone.now()
