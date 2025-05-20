from __future__ import annotations
from typing import TYPE_CHECKING

import base64
import hmac
import logging
import time

from hashlib import sha1
from struct import pack

from django.db import models
from django.db.models.manager import BaseManager
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from idvalid_core.models import get_subid_model

from authn.generators import generate_bytes

if TYPE_CHECKING:
    import datetime


logger = logging.getLogger(__name__)
__all__ = (
    "TOTPDeviceQuerySet",
    "TOTPDeviceManager",
    "TOTPDevice",
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


class TOTPDeviceQuerySet(models.QuerySet):
    pass


_TOTPDeviceManagerBase = models.Manager.from_queryset(
    TOTPDeviceQuerySet
)  # type: type[TOTPDeviceQuerySet]


class TOTPDeviceManager(_TOTPDeviceManagerBase, BaseManager):
    pass


class TOTPDevice(get_subid_model()):
    secret = models.BinaryField(
        _("secret"), max_length=40,
        # validators=[secret_validator],
        default=generate_secret,
        # help_text="A hex-encoded secret key of up to 40 bytes."
    )  # type: bytes
    step = models.PositiveSmallIntegerField(
        _("step"), default=30,
        help_text="The time step in seconds."
    )  # type: int
    start_time = models.DateTimeField(
        _("start time"),
        default=generate_start_time,
        help_text="The datetime at which to begin counting steps."
    )  # type: datetime.datetime
    digits = models.PositiveSmallIntegerField(
        _("digits"),
        choices=[(6, 6), (7, 7), (8, 8), (9, 9)],
        default=6,
        help_text="The number of digits to expect in a token."
    )  # type: int
    tolerance = models.PositiveSmallIntegerField(
        _("tolerance"),
        default=1,
        help_text="The number of time steps in the past or future to allow."
    )  # type: int

    objects = TOTPDeviceManager()

    @property
    def b64_secret(self) -> bytes:
        return base64.b64encode(self.secret)

    @cached_property
    def epoch(self) -> int:
        return int(self.start_time.timestamp())

    def _get_sequence(self, at: int | datetime.datetime = None) -> int:
        if not at:
            at = int(time.time())
        else:
            if not isinstance(at, int):
                at = int(at.timestamp())
            else:
                at = int(at)
        if (diff := (at - self.epoch)) < 0:
            raise ValueError(
                "`for_time` lower than start time")
        return int(diff / self.step)

    def _get_signature(self, sequence: int) -> bytes:
        if sequence < 0:
            raise ValueError("sequence must be positive integer")
        return hmac.new(
            self.secret, pack(b'>Q', sequence), sha1).digest()

    def _generate_token(self, sequence: int) -> int:
        # if sequence < 0:
        #     raise ValueError("sequence must be positive integer")
        # digest = hmac.new(
        #     self.secret, pack(b'>Q', sequence), sha1).digest()
        digest = self._get_signature(sequence)
        offset = digest[-1] & 0xF
        code = (
            (digest[offset] & 0x7F) << 24
            | (digest[offset + 1] & 0xFF) << 16
            | (digest[offset + 2] & 0xFF) << 8
            | (digest[offset + 3] & 0xFF))

        return code % 10 ** self.digits

    def _token_number(self, sequence: int) -> str:
        # the maximum token value is 0x7FFFFFFF
        # which is 2,147,483,647 in decimal
        token = self._generate_token(sequence)
        return str(10_000_000_000 + token)[-self.digits:]

    def get_token(self, *, at: datetime.datetime = None) -> str:
        return self._token_number(self._get_sequence(at=at))

    def verify(
            self, token: str, *,
            at: int | datetime.datetime = None,
            tolerance: int = None) -> bool:
        if at is None:
            at = timezone.now()
        if tolerance is None:
            tolerance = self.tolerance
        sequence = self._get_sequence(at=at)
        encoded_token = token.encode()
        if tolerance:
            for i in range(max(sequence - tolerance, 0), sequence + tolerance):
                if hmac.compare_digest(
                        encoded_token,
                        self._token_number(i).encode()):
                    return True
            return False
        return hmac.compare_digest(
            encoded_token,
            self._token_number(sequence).encode())

    def _token_bytes(self, sequence: int) -> bytes:
        # the maximum token value is 0x7FFFFFFF
        # which is 4 bytes
        token = self._generate_token(sequence)
        return token.to_bytes(4, byteorder="big")

    def get_token_bytes(self, *, at: datetime.datetime = None) -> bytes:
        return self._token_bytes(self._get_sequence(at=at))

    def verify_bytes(
            self, token: bytes, *,
            at: int | datetime.datetime = None,
            tolerance: int = 1) -> bool:
        if at is None:
            at = timezone.now()
        sequence = self._get_sequence(at=at)
        if tolerance:
            for i in range(max(sequence - tolerance, 0), sequence + tolerance):
                if hmac.compare_digest(token, self._token_bytes(i)):
                    return True
            return False
        return hmac.compare_digest(token, self._token_bytes(sequence))
