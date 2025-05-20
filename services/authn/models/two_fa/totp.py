from __future__ import annotations
from typing import TYPE_CHECKING

import base64
import hashlib
import hmac
import logging
import time

from datetime import timedelta
from struct import pack
from urllib.parse import quote, urlencode

from django.db import models
from django.db.models.manager import BaseManager
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from idvalid_core.models import get_subid_model

from authn.generators import generate_bytes
from authn.settings import authn_settings

if TYPE_CHECKING:
    from typing import Callable
    import datetime
    from authn.models import User


logger = logging.getLogger(__name__)
__all__ = (
    "TOTPQuerySet",
    "TOTPManager",
    "TOTP",
)


# def secret_validator(value: str | bytes):
#     try:
#         if isinstance(value, str):
#             value = value.encode()
#
#         unhexlify(value)
#     except Exception:
#         raise ValidationError(
#             '{0} is not valid hex-encoded data.'.format(value))


def generate_secret() -> bytes:
    return generate_bytes(40)


def generate_start_time() -> datetime:
    return timezone.now().replace(microsecond=0)


class TOTPQuerySet(models.QuerySet):
    pass


_TOTPManagerBase = models.Manager.from_queryset(
    TOTPQuerySet
)  # type: type[TOTPQuerySet]


class TOTPManager(_TOTPManagerBase, BaseManager):
    pass


class TOTP(get_subid_model()):
    SHA1_ALGORITHM = "sha1"
    SHA256_ALGORITHM = "sha256"
    SHA512_ALGORITHM = "sha512"
    ALGORITH_CHOICES = (
        (SHA1_ALGORITHM, "SHA1"),
        (SHA256_ALGORITHM, "SHA256"),
        (SHA512_ALGORITHM, "SHA512"),
    )

    DEFAULT_ALGORITHM = SHA1_ALGORITHM
    DEFAULT_DIGITS = 6
    DEFAULT_PERIOD = 30

    secret = models.BinaryField(
        _("secret"), max_length=40,
        # validators=[secret_validator],
        default=generate_secret,
        # help_text="A hex-encoded secret key of up to 40 bytes."
    )  # type: bytes
    algorithm = models.CharField(
        _("algorithm"),
        default=DEFAULT_ALGORITHM,
        choices=ALGORITH_CHOICES,
        max_length=16,
    )  # type: str
    digits = models.PositiveSmallIntegerField(
        _("digits"),
        choices=[(6, 6), (7, 7), (8, 8), (9, 9)],
        default=DEFAULT_DIGITS,
        help_text="The number of digits to expect in a token."
    )  # type: int
    period = models.PositiveSmallIntegerField(
        _("period"),
        default=DEFAULT_PERIOD,
        help_text="The token period in seconds."
    )  # type: int

    t0 = models.BigIntegerField(
        _("t0"),
        default=0,
        help_text="The Unix time at which to begin counting steps."
    )  # type: int
    tolerance = models.PositiveSmallIntegerField(
        _("tolerance"),
        default=1,
        help_text="The number of time steps in the past or future to allow."
    )  # type: int
    drift = models.SmallIntegerField(
        _("drift"),
        default=0,
        help_text=(
            "The number of time steps the prover is known to deviate "
            "from our clock."
        ),
    )  # type: int
    last_t = models.BigIntegerField(
        _("last t"),
        default=-1,
        help_text=(
            "The t value of the latest verified token. "
            "The next token must be at a higher time step."
        ),
    )  # type: int

    confirmed = models.BooleanField(
        _("confirmed"),
        default=False,
        help_text="Is this device ready for use?"
    )  # type: bool
    confirmed_at = models.DateTimeField(
        _("confirmed at"),
        null=True, blank=True,
        help_text="A date and time when this device was confirmed."
    )  # type: datetime.datetime
    description = models.TextField(
        _("description"),
        null=True, blank=True
    )  # type: str

    # Throttling attributes
    failure_timestamp = models.DateTimeField(
        _("failure timestamp"),
        null=True, blank=True,
        help_text=(
            "A timestamp of the last failed verification attempt. "
            "Null if last attempt succeeded."
        ),
    )  # type: datetime.datetime | None
    failure_count = models.PositiveIntegerField(
        _("failure count"),
        default=0,
        help_text="Number of successive failed attempts."
    )  # type: int

    # Timestamp attributes
    last_used_at = models.DateTimeField(
        _("last used at"),
        null=True, blank=True,
        help_text="The most recent date and time this device was used.",
    )  # type: datetime.datetime
    created_at = models.DateTimeField(
        _("created at"),
        auto_now_add=True,
        help_text="The date and time when this device was initially created in the system.",
    )  # type: datetime.datetime
    created_by = models.ForeignKey(
        "authn.User", on_delete=models.SET_NULL,
        verbose_name=_("created by"),
        related_name="created_totp_set",
        null=True, blank=True,
        help_text="The creator of this device.",
    )  # type: User | None

    # disabled attributes
    disabled = models.BooleanField(
        _("disabled"),
        default=False)
    disabled_at = models.DateTimeField(
        _("disabled at"),
        null=True, blank=True)

    objects = TOTPManager()

    @property
    def b64_secret(self) -> bytes:
        return base64.b64encode(self.secret)

    @property
    def b32_secret(self) -> bytes:
        return base64.b32encode(self.secret)

    # ############# #
    # url functions #
    # ############# #
    def get_url_params(self, *, issuer: str = None) -> dict:
        if issuer is None:
            issuer = authn_settings.TOTP_DEFAULT_ISSUER
        params = {
            "secret": self.b32_secret.decode(),
        }
        if issuer:
            params["issuer"] = issuer
        if (algorithm := self.algorithm) != self.DEFAULT_ALGORITHM:
            params["algorithm"] = algorithm.upper()
        if (digits := self.digits) != self.DEFAULT_DIGITS:
            params["digits"] = digits
        if (period := self.period) != self.DEFAULT_PERIOD:
            params["period"] = period
        return params

    def config_url(self, name: str, *, issuer: str = None) -> str:
        params = self.get_url_params(issuer=issuer)
        try:
            label = f"{params["issuer"].replace(":", "")}:{name}"
        except KeyError:
            label = name
        return f"otpauth://totp/{quote(label)}?{urlencode(params)}"

    # ################## #
    # throttle functions #
    # ################## #
    # noinspection PyMethodMayBeStatic
    def get_throttle_factor(self) -> int:
        return authn_settings.TOTP_THROTTLE_FACTOR or 1

    @cached_property
    def throttling_enabled(self) -> bool:
        return bool(self.get_throttle_factor())

    def reset_throttle(self, *, save: bool = True):
        self.failure_timestamp = None
        self.failure_count = 0
        if save:
            self.save(
                update_fields=["failure_timestamp", "failure_count"])

    def increment_throttle(self, *, save: bool = True):
        self.failure_timestamp = timezone.now()
        self.failure_count += 1
        if save:
            self.save(
                update_fields=["failure_timestamp", "failure_count"])

    def verify_is_allowed(self) -> "tuple[bool, dict | None]":
        if (
            self.throttling_enabled
            and self.failure_count > 0
            and self.failure_timestamp is not None
        ):
            now = timezone.now()
            delay = (now - self.failure_timestamp).total_seconds()
            # Required delays should be 1, 2, 4, 8 ...
            delay_required = self.get_throttle_factor() * (
                2 ** (self.failure_count - 1)
            )
            if delay < delay_required:
                return (
                    False,
                    {
                        "reason": "N_FAILED_ATTEMPTS",
                        "failure_count": self.failure_count,
                        "locked_until": (
                            self.failure_timestamp + timedelta(seconds=delay_required)),
                    },
                )

        return True, None

    # ############# #
    # log functions #
    # ############# #
    def set_last_used(self, save: bool = True):
        self.last_used_at = timezone.now()
        if save:
            self.save(update_fields=["last_used_at"])

    # ############## #
    # totp functions #
    # ############## #
    def get_counter(self, at: int | datetime.datetime = None) -> int:
        if at is None:
            at = int(time.time())
        elif not isinstance(at, int):
            at = int(at.timestamp())
        else:
            at = int(at)

        if (diff := (at - self.t0)) < 0:
            raise ValueError("lower than t0")

        return int(diff / self.period)

    def get_signature(self, counter: int) -> bytes:
        if counter < 0:
            raise ValueError("counter must be positive integer")
        return hmac.new(
            self.secret,
            pack(b'>Q', counter),
            getattr(hashlib, self.algorithm)
        ).digest()

    def generate_otp(self, counter: int) -> int:
        digest = self.get_signature(counter)
        offset = digest[-1] & 0xF
        code = (
            (digest[offset] & 0x7F) << 24
            | (digest[offset + 1] & 0xFF) << 16
            | (digest[offset + 2] & 0xFF) << 8
            | (digest[offset + 3] & 0xFF))

        return code % 10 ** self.digits

    # ################ #
    # verify functions #
    # ################ #
    def _verify_success(self, counter: int):
        self.last_t = counter
        self.reset_throttle(save=False)
        self.set_last_used(save=False)
        self.save(update_fields=[
            "last_t",
            # throttle fields
            "failure_timestamp",
            "failure_count",
            # log fields
            "last_used_at",
        ])

    def _verify_failed(self):
        self.increment_throttle()

    def _verify_loop(
            self, validator: Callable[[int], bool], *,
            at: int | datetime.datetime = None,
            tolerance: int = None):
        if at is None:
            at = timezone.now()
        if tolerance is None:
            tolerance = self.tolerance

        counter = self.get_counter(at=at)
        if tolerance:
            window_range = range(
                max(counter - tolerance, self.last_t + 1),
                counter + tolerance + 1)
            for i in window_range:
                if validator(i):
                    self._verify_success(i)
                    return True
            self._verify_failed()
            return False
        elif counter > self.last_t and validator(counter):
            self._verify_success(counter)
            return True
        else:
            self._verify_failed()
            return False

    # #################### #
    # otp number functions #
    # #################### #
    def _token_number(self, counter: int) -> str:
        # the maximum token value is 0x7FFFFFFF
        # which is 2,147,483,647 in decimal
        token = self.generate_otp(counter)
        return str(10_000_000_000 + token)[-self.digits:]

    def get_token(self, *,
                  at: datetime.datetime = None) -> str:
        return self._token_number(self.get_counter(at=at))

    def verify(self, token: str | bytes, *,
               at: int | datetime.datetime = None,
               tolerance: int = None) -> bool:

        if isinstance(token, str):
            token = token.encode()

        def _validate(counter: int) -> bool:
            return hmac.compare_digest(
                token,
                self._token_number(counter).encode())

        return self._verify_loop(_validate, at=at, tolerance=tolerance)

    # ################### #
    # otp bytes functions #
    # ################### #
    def _token_bytes(self, counter: int) -> bytes:
        # the maximum token value is 0x7FFFFFFF
        # which is 4 bytes
        token = self.generate_otp(counter)
        return token.to_bytes(4, byteorder="big")

    def get_token_bytes(self, *, at: datetime.datetime = None) -> bytes:
        return self._token_bytes(self.get_counter(at=at))

    def verify_bytes(
            self, token: bytes, *,
            at: int | datetime.datetime = None,
            tolerance: int = 1) -> bool:

        def _validate(counter: int) -> bool:
            return hmac.compare_digest(token, self._token_bytes(counter))

        return self._verify_loop(_validate, at=at, tolerance=tolerance)

    # ###################### #
    # confirmation functions #
    # ###################### #

    def confirm(self, *, save: bool = True):
        self.confirmed = True
        self.confirmed_at = timezone.now()
        if save:
            self.save(update_fields=[
                "confirmed", "confirmed_at"])

    def disable(self, *, save: bool = True):
        self.disabled = True
        self.disabled_at = timezone.now()
        if save:
            self.save(update_fields=[
                "disabled", "disabled_at"])
