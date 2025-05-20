from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from datetime import datetime, timedelta

from functools import partial
from random import SystemRandom
from string import digits as digit_list

from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.db.models.manager import BaseManager
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from idvalid_core.models import get_subid_model

from authn.settings import authn_settings
from authn.signals import email_otp_post_challenge_create

from .exceptions import ThrottledError, CooldownError, NoPinError

if TYPE_CHECKING:
    from authn.models import User


logger = logging.getLogger(__name__)
__all__ = (
    "generate_token",
    "EmailOTPQuerySet",
    "EmailOTPManager",
    "EmailOTP",
)


# class Expired(TypeError):
#     pass


# class ImmatureError(TypeError):
#     pass


def generate_token(length=6):
    """
    Returns a string of random digits encoded as string.

    :param int length: The number of digits to return.

    :returns: A string of decimal digits.
    :rtype: str

    """
    rand = SystemRandom()

    if hasattr(rand, 'choices'):
        digits = rand.choices(digit_list, k=length)
    else:
        digits = (rand.choice(digit_list) for i in range(length))

    return ''.join(digits)


class EmailOTPQuerySet(models.QuerySet):
    pass


_EmailOTPManagerBase = models.Manager.from_queryset(
    EmailOTPQuerySet
)  # type: type[EmailOTPQuerySet]


class EmailOTPManager(_EmailOTPManagerBase, BaseManager):
    pass


class EmailOTP(get_subid_model()):
    # Device
    user_id: int
    user = models.ForeignKey(
        "authn.User", on_delete=models.CASCADE,
        help_text="The user that this device belongs to.")  # type: User
    name = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text="The human-readable name of this device.")
    confirmed = models.BooleanField(
        default=True,
        help_text="Is this device ready for use?")

    # SideChannelDevice
    _pin: str
    pin = models.CharField(
        _("pin"),
        max_length=128,
        blank=True,
        null=True)
    valid_until = models.DateTimeField(
        _("valid until"),
        default=timezone.now,
        help_text="The timestamp of the moment of expiry of the saved token.")

    # EmailDevice
    email = models.EmailField(
        _("email"),
        max_length=254,
        blank=True,
        null=True,
        help_text='Optional alternative email address to send tokens to')

    # ThrottlingMixin
    throttling_failure_timestamp = models.DateTimeField(
        _("throttling failure timestamp"),
        null=True,
        blank=True,
        default=None,
        help_text=(
            "A timestamp of the last failed verification attempt. Null if last attempt"
            " succeeded."
        ))
    throttling_failure_count = models.PositiveIntegerField(
        _("throttling failure count"),
        default=0,
        help_text="Number of successive failed attempts.")

    # CooldownMixin
    last_generated_timestamp = models.DateTimeField(
        _("last generated timestamp"),
        null=True,
        blank=True,
        help_text="The last time a token was generated for this device.")

    # TimestampMixin
    created_at = models.DateTimeField(
        _("created at"),
        null=True,
        blank=True,
        auto_now_add=True,
        help_text="The date and time when this device was initially created in the system.")
    last_used_at = models.DateTimeField(
        _("last used at"),
        null=True,
        blank=True,
        help_text="The most recent date and time this device was used.")

    objects = EmailOTPManager()

    # def __str__(self):
    #     try:
    #         user = self.user
    #     except ObjectDoesNotExist:
    #         user = None
    #
    #     return "{0} ({1})".format(self.name, user)

    @cached_property
    def cooldown_enabled(self):
        return self.get_cooldown_duration() > 0

    @cached_property
    def throttling_enabled(self):
        return self.get_throttle_factor() > 0

    def get_cooldown_duration(self):
        """
        Returns :setting:`OTP_EMAIL_COOLDOWN_DURATION`.
        """
        return authn_settings.EMAIL_OTP_COOLDOWN_DURATION

    def get_throttle_factor(self):
        """
        Returns :setting:`OTP_EMAIL_THROTTLE_FACTOR`.
        """
        return authn_settings.EMAIL_OTP_THROTTLE_FACTOR

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

    def generate_pin(
            self, *,
            length: int = None,
            duration: int = None):
        if self.last_generated_timestamp is None:
            raise TypeError("not ready")

        if length is None:
            length = authn_settings.EMAIL_OTP_PIN_LENGTH
        if duration is None:
            duration = authn_settings.EMAIL_OTP_PIN_DURATION

        pin = generate_token(length=length)
        self.set_pin(pin, save=False)
        self.valid_until = self.last_generated_timestamp + timedelta(seconds=duration)
        self.save(
            update_fields=["pin", "valid_until"]
        )
        return pin

    def generate_is_allowed(
            self, *,
            current_time: datetime = None) -> bool:
        if current_time is None:
            current_time = timezone.now()

        return (
            not self.last_generated_timestamp
            or (current_time - self.last_generated_timestamp).total_seconds()
            > self.get_cooldown_duration()
        )

    def generate_challenge(
            self, *,
            current_time: datetime = None,
            using: str = None):
        if current_time is None:
            current_time = timezone.now()

        if not self.generate_is_allowed(current_time=current_time):
            raise CooldownError("cooldown pending")

        self.last_generated_timestamp = current_time
        self.save(
            update_fields=["last_generated_timestamp"],
            using=using)
        email_otp_post_challenge_create.send(
            sender=type(self),
            instance=self,
        )
        # self.generate_token(valid_secs=settings.OTP_EMAIL_TOKEN_VALIDITY, commit=True)
        # call signal email otp challenge created

    def check_throttle(self, current_time: datetime):
        if (
            not self.throttling_enabled or
            not self.throttling_failure_count or
            self.throttling_failure_timestamp is None
        ):
            return
        delay = (
                current_time - self.throttling_failure_timestamp
        ).total_seconds()
        # Required delays should be 1, 2, 4, 8 ...
        delay_required = self.get_throttle_factor() * (
                2 ** (self.throttling_failure_count - 1)
        )
        if delay < delay_required:
            raise ThrottledError("throttled")

    def verify(self, pin: str, *, current_time: datetime = None):
        if current_time is None:
            current_time = timezone.now()
        if self.pin is None:
            raise NoPinError("no token supplied")
        self.check_throttle(current_time)

        # if :
        #     raise ImmatureError("immature")
        # if :
        #     raise Expired("expired")

        if (
                current_time < self.last_generated_timestamp or
                current_time >= self.valid_until or
                not self.check_pin(pin)
        ):
            # increment throttle
            self.throttling_failure_timestamp = timezone.now()
            self.throttling_failure_count += 1
            self.save(update_fields=[
                "throttling_failure_timestamp",
                "throttling_failure_count"
            ])
            return False

        # clear pin
        self.pin = None
        # make device expires
        self.valid_until = current_time
        # reset cooldown
        self.last_generated_timestamp = None
        # reset throttle
        self.throttling_failure_timestamp = None
        self.throttling_failure_count = 0
        # set last used
        self.last_used_at = current_time
        self.save(update_fields=[
            "pin",
            "valid_until",
            "last_generated_timestamp",
            "throttling_failure_timestamp",
            "throttling_failure_count",
            "last_used_at",
        ])
        return True
