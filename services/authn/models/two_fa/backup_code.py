from __future__ import annotations
from typing import TYPE_CHECKING

import logging
import secrets

from datetime import datetime

from django.db import models
from django.db.models.manager import BaseManager
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from idvalid_core.models import get_subid_model

from authn.settings import authn_settings

from .exceptions import ThrottledError, CooldownError

if TYPE_CHECKING:
    from authn.models import User


logger = logging.getLogger(__name__)
__all__ = (
    "BackupCodeQuerySet",
    "BackupCodeManager",
    "BackupCode"
)


def generate_codes() -> "list[str]":
    length = int(authn_settings.BACKUP_CODES_LENGTH)
    nbytes = int(authn_settings.BACKUP_CODES_ITEM_BYTES_LENGTH)
    codes = []
    while True:
        item = secrets.token_bytes(nbytes)
        if item not in codes:
            codes.append(item)
            if len(codes) >= length:
                break

    hex_length = nbytes * 2

    def split5(value):
        count = hex_length // 5
        left = hex_length % 5
        if left:
            spaces = [5] * (count + 1)
            spaces[count // 2] = left
        else:
            spaces = [5] * count

        start = 0
        for space in spaces:
            yield value[start: start + space]
            start += space
    return ["-".join(split5(item.hex())) for item in codes]


class BackupCodeQuerySet(models.QuerySet):
    def active(self, *args, **kwargs):
        return self.filter(
            *args, is_active=True, **kwargs)


_BackupCodeManagerBase = models.Manager.from_queryset(
    BackupCodeQuerySet
)  # type: type[BackupCodeQuerySet]


class BackupCodeManager(_BackupCodeManagerBase, BaseManager):
    pass


class BackupCode(get_subid_model()):
    # user_id: int
    # user = models.ForeignKey(
    #     "authn.User", on_delete=models.CASCADE,
    #     related_name="backup_codes",
    #     help_text="The user that this backup code belongs to."
    # )  # type: User

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
        default=timezone.now,
        help_text="The last time a token was generated for this device."
    )  # type: datetime

    codes = models.JSONField(
        _("codes"), default=generate_codes)
    used_codes = models.JSONField(
        _("used codes"), default=list)

    is_active = models.BooleanField(
        _("active flag"), default=True)

    # TimestampMixin
    created_at = models.DateTimeField(
        _("created at"),
        null=True,
        blank=True,
        auto_now_add=True,
        help_text="The date and time when this device was initially created in the system.")
    created_by_id: int | None
    created_by = models.ForeignKey(
        "authn.User", on_delete=models.SET_NULL,
        verbose_name=_("created by"),
        related_name="created_backup_code_set",
        null=True, blank=True,
        help_text="The creator of this backup code.",
    )  # type: User | None
    last_used_at = models.DateTimeField(
        _("last used at"),
        null=True,
        blank=True,
        help_text="The most recent date and time this device was used.")

    objects = BackupCodeManager()

    @property
    def available_codes(self) -> "list[str]":
        used_codes = self.used_codes
        return [
            (
                "-".join([
                    "_" * len(part)
                    for part in code.split("-")
                ])
            ) if code in used_codes else
            code
            for code in self.codes
        ]

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
        return authn_settings.BACKUP_CODES_COOLDOWN_DURATION

    def get_throttle_factor(self):
        """
        Returns :setting:`OTP_EMAIL_THROTTLE_FACTOR`.
        """
        return authn_settings.BACKUP_CODES_THROTTLE_FACTOR

    def regenerate_codes(self):
        pass

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
        self.codes = generate_codes()
        self.used_codes = []
        self.save(
            update_fields=[
                "last_generated_timestamp",
                "codes",
                "used_codes",
            ],
            using=using)

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

    def check_code(self, code: str) -> bool:
        return (
            code in self.codes and
            code not in self.used_codes
        )

    def verify(self, code: str, *, current_time: datetime = None):
        if current_time is None:
            current_time = timezone.now()
        self.check_throttle(current_time)

        if (
                current_time < self.last_generated_timestamp or
                not self.check_code(code)
        ):
            # increment throttle
            self.throttling_failure_timestamp = timezone.now()
            self.throttling_failure_count += 1
            self.save(update_fields=[
                "throttling_failure_timestamp",
                "throttling_failure_count"
            ])
            return False

        # reset throttle
        self.throttling_failure_timestamp = None
        self.throttling_failure_count = 0
        # set last used
        self.last_used_at = current_time
        # set used code
        self.used_codes.append(code)
        self.save(update_fields=[
            "throttling_failure_timestamp",
            "throttling_failure_count",
            "last_used_at",
            "used_codes",
        ])
        return True

    def disable(self, save: bool = True):
        self.is_active = False
        if save:
            self.save(update_fields=["is_active"])
