from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from base64 import b64encode
from datetime import timedelta
from hashlib import sha256

from functools import partial
from random import SystemRandom
from string import digits as digit_list

from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.db.models.manager import BaseManager
# from django.utils.functional import cached_property
from django.utils.crypto import constant_time_compare
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from idvalid_core.models import get_subid_model

from authn.settings import authn_settings
# from authn.signals import email_otp_post_challenge_create

# from .exceptions import ThrottledError, CooldownError, NoPinError

if TYPE_CHECKING:
    from typing import Self
    from datetime import datetime
    from authn.models import User


logger = logging.getLogger(__name__)
__all__ = (
    "MobileOTPQuerySet",
    "MobileOTPManager",
    "MobileOTP",
)


def generate_pin(length: int = None):
    """
    Returns a string of random digits encoded as string.

    :param int length: The number of digits to return.

    :returns: A string of decimal digits.
    :rtype: str

    """
    rand = SystemRandom()
    if length is None:
        length = authn_settings.MOBILE_OTP_PIN_LENGTH

    if hasattr(rand, 'choices'):
        digits = rand.choices(digit_list, k=length)
    else:
        digits = (rand.choice(digit_list) for i in range(length))

    return ''.join(digits)


def generate_valid_time(duration: int = None) -> datetime:
    if duration is None:
        duration = int(authn_settings.MOBILE_OTP_PIN_DURATION)
    return timezone.now() + timedelta(seconds=duration)


class MobileOTPQuerySet(models.QuerySet):
    def create(self, pin: str = None, **kwargs):
        """
        Create a new object with the given kwargs, saving it to the database
        and returning the created object.
        """
        if pin is None:
            pin = generate_pin()
        obj = self.model(pin=pin, **kwargs)  # type: MobileOTP
        obj.set_pin(pin, save=False)
        self._for_write = True
        obj.save(force_insert=True, using=self.db)
        return obj

    def alive(self, *args, **kwargs) -> Self:
        return self.filter(
            *args,
            valid_until__gte=timezone.now(),
            confirmed=False,
            **kwargs)

    def confirmed(self, *args, **kwargs) -> Self:
        return self.filter(
            *args,
            confirmed=True,
            **kwargs)

    def accepted(self, *args, **kwargs) -> Self:
        return self.confirmed(
            *args,
            accepted=True,
            **kwargs)


_MobileOTPManagerBase = models.Manager.from_queryset(
    MobileOTPQuerySet
)  # type: type[MobileOTPQuerySet]


class MobileOTPManager(_MobileOTPManagerBase, BaseManager):
    pass


class MobileOTP(get_subid_model()):
    # Device
    user_id: int
    user = models.ForeignKey(
        "authn.User", on_delete=models.CASCADE,
        help_text="The user that this device belongs to.")  # type: User

    # SideChannelDevice
    _pin: str = None
    pin = models.CharField(
        _("pin"),
        max_length=128,
        blank=True,
        null=True)
    valid_until = models.DateTimeField(
        _("valid until"),
        default=generate_valid_time,
        help_text="The timestamp of the moment of expiry of the saved token.")
    state = models.BinaryField(
        _("state"),
        null=True, blank=True,
        max_length=32)
    confirmed = models.BooleanField(
        _("confirmed status"),
        default=False)
    accepted = models.BooleanField(
        _("accepted status"),
        default=False)

    # TimestampMixin
    created_at = models.DateTimeField(
        _("created at"),
        null=True,
        blank=True,
        auto_now_add=True,)

    objects = MobileOTPManager()

    def set_pin(
            self, raw_pin: str, *,
            hold: bool = True,
            save: bool = True):
        self.pin = make_password(raw_pin)
        if hold:
            self._pin = raw_pin
        if save:
            self.save(update_fields=["pin"])

    def check_pin(self, raw_pin: str) -> bool:
        return check_password(
            raw_pin, self.pin,
            partial(self.set_pin, hold=False))

    def check_state(self, state: str) -> bool:
        print(
            state,
            sha256(state.encode()).digest(),
            self.state
        )
        # noinspection InsecureHash
        return constant_time_compare(
            sha256(state.encode()).digest(),
            self.state)

    # def generate_pin(
    #         self, *,
    #         length: int = None,
    #         duration: int = None):
    #     if self.last_generated_timestamp is None:
    #         raise TypeError("not ready")
    #
    #     if length is None:
    #         length = authn_settings.EMAIL_OTP_PIN_LENGTH
    #     if duration is None:
    #         duration = authn_settings.EMAIL_OTP_PIN_DURATION
    #
    #     pin = generate_token(length=length)
    #     self.set_pin(pin, save=False)
    #     self.valid_until = self.last_generated_timestamp + timedelta(seconds=duration)
    #     self.save(
    #         update_fields=["pin", "valid_until"]
    #     )
    #     return pin
    #
    # def generate_is_allowed(
    #         self, *,
    #         current_time: datetime = None) -> bool:
    #     if current_time is None:
    #         current_time = timezone.now()
    #
    #     return (
    #         not self.last_generated_timestamp
    #         or (current_time - self.last_generated_timestamp).total_seconds()
    #         > self.get_cooldown_duration()
    #     )
    #
    # def generate_challenge(
    #         self, *,
    #         current_time: datetime = None,
    #         using: str = None):
    #     if current_time is None:
    #         current_time = timezone.now()
    #
    #     if not self.generate_is_allowed(current_time=current_time):
    #         raise CooldownError("cooldown pending")
    #
    #     self.last_generated_timestamp = current_time
    #     self.save(
    #         update_fields=["last_generated_timestamp"],
    #         using=using)
    #     email_otp_post_challenge_create.send(
    #         sender=type(self),
    #         instance=self,
    #     )
    #     # self.generate_token(valid_secs=settings.OTP_EMAIL_TOKEN_VALIDITY, commit=True)
    #     # call signal email otp challenge created
    #
    # def check_throttle(self, current_time: datetime):
    #     if (
    #         not self.throttling_enabled or
    #         not self.throttling_failure_count or
    #         self.throttling_failure_timestamp is None
    #     ):
    #         return
    #     delay = (
    #             current_time - self.throttling_failure_timestamp
    #     ).total_seconds()
    #     # Required delays should be 1, 2, 4, 8 ...
    #     delay_required = self.get_throttle_factor() * (
    #             2 ** (self.throttling_failure_count - 1)
    #     )
    #     if delay < delay_required:
    #         raise ThrottledError("throttled")

    def verify(self, pin: str):
        self.confirmed = True
        self.accepted = self.check_pin(pin)
        self.save(update_fields=[
            "confirmed",
            "accepted",
        ])
        return self.accepted

    def reject(self):
        self.confirmed = True
        self.save(update_fields=[
            "confirmed",
        ])
