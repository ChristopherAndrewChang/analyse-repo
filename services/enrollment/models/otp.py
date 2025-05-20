from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.db.models.manager import BaseManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from idvalid_core.models import get_subid_model

from evercore_grpc.utils import timestamp_to_datetime

from enrollment.integration.rpc import verify_otp_signature

from . import constants

if TYPE_CHECKING:
    from .enrollment import Enrollment


logger = logging.getLogger(__name__)
__all__ = (
    "OtpQuerySet",
    "OtpManager",
    "Otp",
)


class OtpQuerySet(models.QuerySet):
    def create(self, enrollment: Enrollment | str, device_id: str, state: str, **kwargs) -> Otp:
        if isinstance(enrollment, str):
            from .enrollment import Enrollment
            enrollment = Enrollment.objects.create(
                email=enrollment, include_otp=True,
                otp_kwargs={
                    "device_id": device_id
                }
            )
            otp_data = enrollment.otp_response
        else:
            otp_data = enrollment.refresh_otp(device_id=device_id)
        kwargs["otp_id"] = otp_data.id
        kwargs["expires"] = timestamp_to_datetime(otp_data.expires)
        kwargs["key"] = otp_data.key
        return super().create(
            enrollment=enrollment, device_id=device_id,
            state=make_password(state),
            **kwargs)


_OtpManagerBase = models.Manager.from_queryset(
    OtpQuerySet
)  # type: type[OtpQuerySet]


class OtpManager(_OtpManagerBase, BaseManager):
    pass


class Otp(get_subid_model()):
    _raw_state: str

    enrollment = models.ForeignKey(
        "enrollment.Enrollment", on_delete=models.CASCADE,
        related_name="otp_set",
        verbose_name=_("enrollment"))  # type: Enrollment

    # security
    device_id = models.CharField(
        _("device id"), max_length=constants.DEVICE_ID_LENGTH)
    state = models.CharField(
        _("state"), max_length=128)
    user_agent = models.CharField(
        _("user agent"), max_length=512)

    # otp
    otp_id = models.CharField(
        _("otp id"), max_length=constants.OTP_ID_LENGTH)
    expires = models.DateTimeField(
        _("expired date"))
    key = models.BinaryField(
        _("key"))

    # internal flags
    is_confirmed = models.BooleanField(
        _("confirmed flag"), default=False, editable=False)
    confirmed_date = models.DateTimeField(
        _("confirmed date"), null=True, blank=True, editable=False)

    # logs
    created = models.DateTimeField(
        _("created"), auto_now_add=True, editable=False)

    objects = OtpManager()

    def is_active(self) -> bool:
        return (
            timezone.now() < self.expires and
            self.enrollment.last_otp_id == self.otp_id)

    def set_state(self, raw_value: str):
        self.state = make_password(raw_value)
        self._raw_state = raw_value

    def check_state(self, raw_value: str) -> bool:
        def upgrade(value: str):
            self.set_state(value)
            self._raw_state = None
            self.save(update_fields=["state"])
        return check_password(raw_value, self.state, upgrade)

    def verify(self, signature: bytes) -> bool:
        return verify_otp_signature(
            instance=self, signature=signature)

    def confirm(self, *, save: bool = True):
        if self.is_confirmed:
            raise TypeError("already confirmed")
        self.enrollment.register(save=save)
        self.is_confirmed = True
        self.confirmed_date = timezone.now()
        if save:
            self.save(update_fields=["is_confirmed", "confirmed_date"])
