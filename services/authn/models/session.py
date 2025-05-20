from __future__ import annotations

from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from evercore_jwt_auth.settings import jwt_auth_settings
from evercore_jwt_auth.utils import datetime_to_epoch

from authn.settings import authn_settings
from authn.signals import session_revoke

from idvalid_core.models import get_subid_model

from . import constants

if TYPE_CHECKING:
    from datetime import datetime
    from authn.models import (
        User,
        Platform,
        RefreshTokenManager,
        RefreshToken,
    )


logger = logging.getLogger(__name__)
__all__ = (
    "SessionQuerySet",
    "SessionManager",
    "Session",
)


class SessionQuerySet(models.QuerySet):
    def login(
            self, user: User, platform: Platform, device_id: str,
    ) -> Session:
        now = timezone.now()
        instance, created = self.get_or_create(
            user=user,
            platform=platform,
            device_id=device_id,
            defaults={
                "last_auth_time": now,
                "is_mobile": platform.is_mobile()
            }
        )
        if not created:
            instance.update_last_auth_time(current_time=now)
        return instance


_SessionManagerBase = models.Manager.from_queryset(
    SessionQuerySet
)  # type: type[SessionQuerySet]


class SessionManager(_SessionManagerBase, BaseManager):
    pass


class Session(get_subid_model()):
    # related manager annotations
    refresh_tokens: RefreshTokenManager

    user_id: int
    user = models.ForeignKey(
        "authn.User", on_delete=models.CASCADE,
        verbose_name=_("user"),
        related_name="sessions",
    )  # type: User
    platform_id: int
    platform = models.ForeignKey(
        "authn.Platform", on_delete=models.CASCADE,
        verbose_name=_("platform"),
        related_name="sessions",
    )  # type: Platform
    device_id = models.CharField(
        _("device id"),
        max_length=constants.DEVICE_ID_LENGTH)
    last_auth_time = models.DateTimeField(
        _("last auth time"),
        null=True, blank=True)
    is_mobile = models.BooleanField(
        _("mobile status"),
        default=False)

    created_at = models.DateTimeField(
        _("created at"),
        auto_now_add=True)
    updated_at = models.DateTimeField(
        _("updated at"),
        auto_now=True)

    objects = SessionManager()

    class Meta:
        unique_together = (
            ("user", "platform", "device_id"),
        )

    def generate_refresh_token(self, mfa_required: bool, *, mfa_ref: str = None) -> RefreshToken:
        extra = {
            jwt_auth_settings.AUTHN_PLATFORM_TYPE_CLAIM: self.platform.platform_type
        }
        if auth_time := self.last_auth_time:
            extra["auth_time"] = datetime_to_epoch(auth_time)
        claims = {
            "subject": self.user_id,
            "audience": self.platform.subid,
            "multi_factor_auth": not mfa_required,
            "extra_claims": extra
        }
        if not mfa_required:
            claims["multi_factor_ref"] = mfa_ref
            lifetime = jwt_auth_settings.AUTHN_MULTI_FACTOR_SESSION_LIFETIME
            claims["multi_factor_expires"] = timezone.now() + lifetime
        return self.refresh_tokens.create(**claims)

    def update_last_auth_time(
            self, *,
            current_time: datetime = None,
            save: bool = True):
        if current_time is None:
            current_time = timezone.now()
        self.last_auth_time = current_time
        if save:
            self.save(update_fields=["last_auth_time"])

    def revoke(self):
        session_revoke.send(sender=self.__class__, instance=self)
