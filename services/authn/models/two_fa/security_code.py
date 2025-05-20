from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from datetime import timedelta
from functools import partial

from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.db.models.manager import BaseManager
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from idvalid_core.models import get_subid_model

from authn.settings import authn_settings

if TYPE_CHECKING:
    import datetime
    from authn.models import User


logger = logging.getLogger(__name__)
__all__ = (
    "SecurityCodeQuerySet",
    "SecurityCodeManager",
    "SecurityCode",
)


class SecurityCodeQuerySet(models.QuerySet):
    def create(self, pin: str, **kwargs) -> SecurityCode:
        pin = make_password(pin)
        return super().create(pin=pin, **kwargs)


_SecurityCodeManagerBase = models.Manager.from_queryset(
    SecurityCodeQuerySet
)  # type: type[SecurityCodeQuerySet]


class SecurityCodeManager(_SecurityCodeManagerBase, BaseManager):
    pass


class SecurityCode(get_subid_model()):
    pin = models.CharField(
        _("pin"),
        max_length=128)

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
        related_name="created_security_code_set",
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

    objects = SecurityCodeManager()

    def get_throttle_factor(self) -> int:
        return authn_settings.SECURITY_CODE_THROTTLE_FACTOR or 1

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

    def set_last_used(self, save: bool = True):
        self.last_used_at = timezone.now()
        if save:
            self.save(update_fields=["last_used_at"])

    def update_pin(self, raw_pin: str, *,
                   hold_raw_pin: bool = True,
                   save: bool = True):
        self.pin = make_password(raw_pin)
        self._pin = raw_pin if hold_raw_pin else None
        if save:
            self.save(update_fields=["pin"])

    def check_pin(self, raw_pin: str) -> bool:
        return check_password(
            raw_pin, self.pin,
            partial(self.update_pin, hold_raw_pin=False))

    def _verify_success(self):
        self.reset_throttle(save=False)
        self.set_last_used(save=False)
        self.save(update_fields=[
            # throttle fields
            "failure_timestamp",
            "failure_count",
            # log fields
            "last_used_at",
        ])

    def _verify_failed(self):
        self.increment_throttle()

    def verify(self, raw_pin: str) -> bool:
        allowed, _ = self.verify_is_allowed()
        if not allowed:
            return False

        if self.check_pin(raw_pin):
            self._verify_success()
            return True
        self._verify_failed()
        return False

    def disable(self, *, save: bool = True):
        self.disabled = True
        self.disabled_at = timezone.now()
        if save:
            self.save(update_fields=[
                "disabled", "disabled_at"])
