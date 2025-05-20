from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from authn.models import (
        User,
        TOTP,
        SecurityCode,
        BackupCode,
    )


logger = logging.getLogger(__name__)
__all__ = (
    "UserMFAQuerySet",
    "UserMFAManager",
    "UserMFA",
)


class UserMFAQuerySet(models.QuerySet):
    pass


_UserMFAManagerBase = models.Manager.from_queryset(
    UserMFAQuerySet
)  # type: type[UserMFAQuerySet]


class UserMFAManager(_UserMFAManagerBase, BaseManager):
    pass


class UserMFA(models.Model):
    user_id: int
    user = models.OneToOneField(
        "authn.User", on_delete=models.CASCADE,
        primary_key=True,
        related_name="mfa",
        verbose_name=_("user"),
    )  # type: User

    totp_id: int | None
    totp = models.ForeignKey(
        "authn.TOTP", on_delete=models.SET_NULL,
        verbose_name=_("totp"),
        null=True, blank=True
    )  # type: TOTP | None
    security_code_id: int | None
    security_code = models.ForeignKey(
        "authn.SecurityCode", on_delete=models.SET_NULL,
        verbose_name=_("security code"),
        null=True, blank=True
    )  # type: SecurityCode | None
    backup_code_id: int | None
    backup_code = models.ForeignKey(
        "authn.BackupCode", on_delete=models.SET_NULL,
        verbose_name=_("backup code"),
        null=True, blank=True
    )  # type: BackupCode | None
    passkey_device_count = models.PositiveIntegerField(
        _("passkey device count"), default=0
    )  # type: int
    mobile_logged_in_count = models.PositiveIntegerField(
        _("mobile logged in count"), default=0
    )  # type: int

    objects = UserMFAManager()

    def has_totp(self) -> bool:
        return self.totp_id is not None

    def set_totp(self, totp: TOTP, *, save: bool = True):
        if self.has_totp():
            self.totp.disable(save=save)
        totp.confirm(save=save)
        self.totp = totp
        if save:
            self.save(update_fields=["totp"])

    def remove_totp(self, *, save: bool = True):
        if self.has_totp():
            self.totp.disable(save=save)
        self.totp = None
        if save:
            self.save(update_fields=["totp"])

    def has_security_code(self) -> bool:
        return self.security_code_id is not None

    def set_security_code(
            self, security_code: SecurityCode, *,
            save: bool = True):
        if self.has_security_code():
            self.security_code.disable(save=save)
        self.security_code = security_code
        if save:
            self.save(update_fields=["security_code"])

    def remove_security_code(self, *, save: bool = True):
        if self.has_security_code():
            self.security_code.disable(save=save)
        self.security_code = None
        if save:
            self.save(update_fields=["security_code"])

    def has_backup_code(self) -> bool:
        return self.backup_code_id is not None

    def set_backup_code(
            self, value: BackupCode, *,
            save: bool = True):
        if self.has_backup_code():
            self.backup_code.disable(save=save)
        self.backup_code = value
        if save:
            self.save(update_fields=["backup_code"])

    def remove_backup_code(self, *, save: bool = True):
        if self.has_backup_code():
            self.backup_code.disable(save=save)
        self.backup_code = None
        if save:
            self.save(update_fields=["backup_code"])

    def has_passkey(self) -> bool:
        return self.passkey_device_count > 0

    def inc_passkey_device(self):
        self.passkey_device_count = models.F("passkey_device_count") + models.Value(1)
        self.save(update_fields=["passkey_device_count"])

    def dec_passkey_device(self):
        self.passkey_device_count = models.F("passkey_device_count") - models.Value(1)
        self.save(update_fields=["passkey_device_count"])

    def has_mobile_logged_in(self) -> bool:
        return self.mobile_logged_in_count > 0

    def inc_mobile_logged_in(self):
        self.mobile_logged_in_count = models.F("mobile_logged_in_count") + models.Value(1)
        self.save(update_fields=["mobile_logged_in_count"])

    def dec_mobile_logged_in(self):
        self.mobile_logged_in_count = models.F("mobile_logged_in_count") - models.Value(1)
        self.save(update_fields=["mobile_logged_in_count"])

    @property
    def summary(self) -> dict:
        return {
            "authenticator": self.has_totp(),
            "security_code": self.has_security_code(),
            "passkey": self.has_passkey(),
            "backup_code": self.has_backup_code(),
            "mobile_logged_in": self.has_mobile_logged_in()
        }
