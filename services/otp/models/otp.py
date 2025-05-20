from __future__ import annotations
from typing import TYPE_CHECKING

import logging
import math

from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.db import models
from django.db.models.manager import BaseManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from idvalid_core.models import get_subid_model

from idvalid_integration.protos.models.otp_pb2 import CreateOtp, Method

from otp import signals
from otp.generators import pin_number, default_expires, generate_token
from otp.settings import otp_settings
from otp.twilio import twilio

from .recipient2 import Recipient2
from . import constants

if TYPE_CHECKING:
    from typing import Self


logger = logging.getLogger(__name__)
__all__ = (
    "OtpQuerySet",
    "OtpManager",
    "Otp",
)


EMAIL_ADDRESS_FIELD = "email_address"
PHONE_NUMBER_FIELD = "phone_number"
USER_ID_FIELD = "user_id"

otp_method_map = {
    Method.METHOD_MAIL: EMAIL_ADDRESS_FIELD,
    Method.METHOD_SMS: PHONE_NUMBER_FIELD,
    Method.METHOD_WHATSAPP: PHONE_NUMBER_FIELD,
    Method.METHOD_IDVALID: USER_ID_FIELD,
}


recipient_type_field_map = {
    EMAIL_ADDRESS_FIELD: Recipient2.EMAIL_RECIPIENT_TYPE,
    PHONE_NUMBER_FIELD: Recipient2.PHONE_RECIPIENT_TYPE,
    USER_ID_FIELD: Recipient2.USER_RECIPIENT_TYPE
}


class OtpQuerySet(models.QuerySet):
    def create_from_message(self, message: CreateOtp) -> Otp:
        method = message.method
        recipient_field = message.WhichOneof("recipient")
        if otp_method_map[method] != recipient_field:
            raise ValueError("invalid recipient type")
        recipient, _ = Recipient2.objects.get_or_create(
            value=getattr(message, recipient_field),
            recipient_type=recipient_type_field_map[recipient_field])
        expires = (
            message.expires.ToDatetime()
            if message.HasField("expires") else
            default_expires())

        return self.create(
            object_id=message.object_id,
            usage=message.usage,
            ref_id=message.ref_id,
            method=message.method,
            device_id=message.device_id,
            user_agent=message.user_agent,
            owner_id=message.owner_id or None,
            expires=expires,
            recipient=recipient)

    def ready(self, *args, **kwargs) -> Self:
        return self.filter(
            *args, pin__isnull=False, **kwargs)

    def active(self, *args, **kwargs) -> Self:
        return self.filter(
            *args, pin__isnull=False,
            suppressed=False, applied=False, **kwargs)

    def suppress(self, ref_id: str) -> int:
        return self.filter(
            ref_id=ref_id,
            applied=False,
            suppressed=False,
        ).update(
            suppressed=True,
            suppressed_time=timezone.now())

    def apply(self) -> int:
        return self.filter(applied=False).update(
            applied=True,
            applied_time=timezone.now())

    def applied(self) -> Self:
        return self.filter(applied=True)


_OtpManagerBase = models.Manager.from_queryset(
    OtpQuerySet
)  # type: type[OtpQuerySet]


class OtpManager(_OtpManagerBase, BaseManager):
    pass


class Otp(get_subid_model()):
    METHOD_CHOICES = (
        (Method.METHOD_MAIL, "Mail"),
        (Method.METHOD_SMS, "SMS"),
        (Method.METHOD_WHATSAPP, "Whatsapp"),
        (Method.METHOD_IDVALID, "IDValid"),
    )

    # lookup fields
    object_id = models.CharField(
        _("object id"),
        max_length=constants.OBJECT_ID_LENGTH)
    usage = models.CharField(
        _("usage"), max_length=64)

    # security fields
    ref_id = models.CharField(
        _("ref id"),
        max_length=constants.REF_ID_LENGTH, db_index=True)
    device_id = models.CharField(
        _("device id"), max_length=constants.DEVICE_ID_LENGTH)
    user_agent = models.TextField(
        _("user agent"))
    expires = models.DateTimeField(
        _("expires"))
    owner_id = models.BigIntegerField(
        _("owner id"),
        null=True, blank=True)

    # recipient fields
    method = models.PositiveSmallIntegerField(
        _("method"),
        choices=METHOD_CHOICES,
        db_index=True)
    recipient = models.ForeignKey(
        "otp.Recipient2", on_delete=models.CASCADE,
        verbose_name=_("recipient"))  # type: Recipient2

    token = models.TextField(
        _("token"), max_length=(
            math.ceil(otp_settings.DEFAULT_OTP_TOKEN_BYTES_LENGTH / 3 * 4)
        ), null=True, blank=True)

    pin = models.CharField(
        _("pin"),
        max_length=128, null=True, editable=False)
    twilio_verification_sid = models.TextField(
        _("twilio verification sid"),
        null=True, blank=True)

    applied = models.BooleanField(
        _("applied"), default=False)
    applied_time = models.DateTimeField(
        _("applied time"), null=True, blank=True)

    suppressed = models.BooleanField(
        _("suppressed"), default=False)
    suppressed_time = models.DateTimeField(
        _("suppressed time"), null=True, blank=True)

    created = models.DateTimeField(
        _("created"), auto_now_add=True)

    objects = OtpManager()

    class Meta:
        unique_together = ("object_id", "usage")

    def is_expired(self) -> bool:
        return timezone.now() > self.expires

    def is_ready(self) -> bool:
        return (
                self.pin is not None or
                self.twilio_verification_sid is not None
        )

    def set_pin(self, raw_pin: str):
        self.pin = make_password(raw_pin)
        self._pin = raw_pin

    def prepare_pin(self, *, save: bool = True) -> str:
        pin = pin_number()
        self.set_pin(pin)
        if save:
            self.save(update_fields=["pin"])
        return pin

    def check_pin(self, raw_pin: str) -> bool:
        if not self.is_ready():
            return False

        def upgrade(value: str):
            self.set_pin(value)
            self._pin = None
            self.save(update_fields=["pin"])

        return check_password(raw_pin, self.pin, upgrade)

    def send(self):
        if self.is_ready():
            raise TypeError("already sent")

        recipient = self.recipient
        method = self.method
        if method == Method.METHOD_MAIL:
            msg=f"Your (IDValid) verification code is: {self.prepare_pin()}"
            print(msg)
            send_mail(
                subject="IDValid PIN",
                message=msg,
                from_email=None,
                recipient_list=[recipient.value])
        elif method == Method.METHOD_SMS:
            response = twilio.send_otp(self.recipient.value)
            self.twilio_verification_sid = response.sid
            self.save(update_fields=["twilio_verification_sid"])

    def verify(self, code: str) -> bool:
        method = self.method
        if method == Method.METHOD_MAIL:
            return self.check_pin(code)
        elif method == Method.METHOD_SMS:
            return twilio.verify_otp(self.twilio_verification_sid, code)
        raise TypeError(f"unknown method {method}")

    def apply(self, *, save: bool = True, using: str = None):
        if self.applied:
            raise TypeError("already applier")
        self.applied = True
        self.applied_time = timezone.now()
        self.token = generate_token()
        if save:
            self.save(
                update_fields=["applied", "applied_time", "token"],
                using=using)
            signals.otp_applied.send(
                sender=self.__class__, instance=self, using=self._state.db)

    def suppress(self, *, save: bool = True, using: str = None):
        if self.suppressed:
            raise TypeError("already suppressed")
        self.suppressed = True
        self.suppressed_time = timezone.now()
        if save:
            self.save(
                update_fields=["suppressed", "suppressed_time"],
                using=using)
            signals.otp_suppressed.send(
                sender=self.__class__, instance=self, using=self._state.db)
