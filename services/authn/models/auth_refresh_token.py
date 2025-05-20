from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from idvalid_core.models import get_subid_model

from .constants import ALGORITHM_TYPES

if TYPE_CHECKING:
    from authn.models import Platform, Session


logger = logging.getLogger(__name__)
__all__ = (
    "AuthRefreshTokenQuerySet",
    "AuthRefreshTokenManager",
    "AuthRefreshToken",
)


class AuthRefreshTokenQuerySet(models.QuerySet):
    pass


_AuthRefreshTokenManagerBase = models.Manager.from_queryset(
    AuthRefreshTokenQuerySet
)  # type: type[AuthRefreshTokenQuerySet]


class AuthRefreshTokenManager(_AuthRefreshTokenManagerBase, BaseManager):
    pass


class AuthRefreshToken(get_subid_model()):
    # PAYLOAD
    # subid => "jti" (JWT ID) Claim
    issuer = models.CharField(
        _("issuer"), max_length=256,
        help_text=_('"iss" (Issuer) Claim.'))
    subject = models.CharField(
        _("subject"), max_length=256,
        help_text=_('"sub" (Subject) Claim.'))
    expired_time = models.DateTimeField(
        _("expired time"),
        help_text=_('"exp" (Expiration Time) Claim.'))
    created_time = models.DateTimeField(
        _("created time"), auto_now_add=True,
        help_text=_('"iat" (Issued At) Claim.'))

    platform_id: int
    platform = models.ForeignKey(
        "authn.Platform", on_delete=models.CASCADE,
        verbose_name=_("platform"),
        help_text=_('"aud" (Audience) Claim.')
    )  # type: Platform
    session_id: int
    session = models.ForeignKey(
        "authn.Session", on_delete=models.CASCADE,
        verbose_name=_("session"),
    )  # type: Session
    extra_claims = models.JSONField(
        _("extra claims"), null=True, blank=True,
        help_text=_("For more extra claims."))

    # HEADERS
    algorithm = models.CharField(
        _("algorithm"), max_length=8, choices=ALGORITHM_TYPES)
    extra_headers = models.JSONField(
        _("extra headers"), null=True, blank=True)

    token = models.CharField(
        _("token"), max_length=256)
    revoked_time = models.DateTimeField(
        _("revoked time"), null=True, blank=True,
        help_text=_("When this refresh token was revoked."))

    objects = AuthRefreshTokenManager()

    def get_access_token(self, claims):
        pass

    def revoke(self):
        self.revoked_time = timezone.now()
        self.save(update_fields=["revoked_time"])
