from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from uuid import uuid4

from django.apps import apps
from django.db import models
from django.db.models.manager import BaseManager

from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from evercore_jwt.settings import jwt_settings

from evercore_jwt_auth.settings import jwt_auth_settings
from evercore_jwt_auth.utils import datetime_to_epoch

from idvalid_core.models import get_subid_model

from authn.settings import authn_settings

from authn.models import constants

from .plugin_base import RefreshTokenPluginBase

if TYPE_CHECKING:
    from typing import Sequence, Any
    import datetime
    from django.db.models.fields.reverse_related import (
        ForeignObjectRel,
    )
    from authn.tokens import (
        RefreshToken as RefreshTokenObject,
        AccessToken as AccessTokenObject,
    )
    from authn.models import Session


logger = logging.getLogger(__name__)
__all__ = (
    "RefreshTokenQuerySet",
    "RefreshTokenManager",
    "RefreshToken",
)


def set_default_issuer_claim(claims: dict):
    if constants.JWT_ISSUER_CLAIM not in claims:
        claims[constants.JWT_ISSUER_CLAIM] = authn_settings.JWT_ISSUER


def generate_jwt_id() -> str:
    return uuid4().hex


def is_plugin(descriptor: ForeignObjectRel) -> bool:
    return descriptor.one_to_one and issubclass(
        descriptor.related_model,
        RefreshTokenPluginBase,
    )


class PluginManager:
    @cached_property
    def plugin_map(self) -> dict[str, type[RefreshTokenPluginBase]]:
        # make sure all models already loaded
        apps.check_apps_ready()

        return {
            name: descriptor.related_model
            for name, descriptor in RefreshToken._meta.fields_map.items()
            if is_plugin(descriptor)
        }

    @property
    def available_plugins(self) -> Sequence[str]:
        return tuple(self.plugin_map.keys())

    def get_extra_claims(
            self, instance: RefreshToken, plugin_name: str) -> dict[str, Any]:
        try:
            model = self.plugin_map[plugin_name]
        except KeyError:
            return {}
        try:
            related = model.objects.get(
                refresh_token_id=instance.pk)  # type: RefreshTokenPluginBase
        except model.DoesNotExist:
            return {}
        return related.get_extra_claims()

    def set_plugin_object(
            self, instance: RefreshToken, plugin_name: str, **kwargs
    ) -> RefreshTokenPluginBase :
        model = self.plugin_map[plugin_name]
        result, created = model.objects.get_or_create(
            refresh_token=instance,
            defaults=kwargs
        )  # type: RefreshTokenPluginBase, bool
        if not created:
            for key, val in kwargs.items():
                setattr(result, key, val)
            result.save(update_fields=tuple(kwargs.keys()))
        return result


plugin_manager = PluginManager()


class RefreshTokenQuerySet(models.QuerySet):
    pass


_RefreshTokenManagerBase = models.Manager.from_queryset(
    RefreshTokenQuerySet
)  # type: type[RefreshTokenQuerySet]


class RefreshTokenManager(_RefreshTokenManagerBase, BaseManager):
    pass


class RefreshToken(get_subid_model()):
    session_id: int
    session = models.ForeignKey(
        "authn.Session", on_delete=models.CASCADE,
        related_name="refresh_tokens",
        verbose_name=_("session"))  # type: Session

    subject = models.CharField(
        _("subject"), max_length=64,
        null=True, blank=True)
    audience = models.CharField(
        _("audience"), max_length=64,
        null=True, blank=True)
    not_before = models.DateTimeField(
        _("not before"), null=True, blank=True
    )  # type: datetime.datetime
    issued_at = models.DateTimeField(
        _("issued at"), auto_now_add=True
    )  # type: datetime.datetime
    multi_factor_auth = models.BooleanField(
        _("multi factor authentication"),
        default=False)
    multi_factor_expires = models.DateTimeField(
        _("multi factor expiration date"),
        null=True, blank=True,
    )  # type: datetime.datetime
    multi_factor_ref = models.CharField(
        _("multi factor reference"),
        max_length=64,
        null=True, blank=True)

    extra_claims = models.JSONField(
        _("extra claims"), null=True, blank=True
    )  # type: dict | None
    plugins = models.JSONField(
        _("plugin in "),
        null=True, blank=True
    )  # type: list | None

    objects = RefreshTokenManager()

    @property
    def expired_time(self) -> datetime.datetime:
        if (start_time := self.not_before) is None:
            start_time = self.issued_at
        return start_time + jwt_auth_settings.REFRESH_TOKEN_LIFETIME

    @property
    def is_alive(self) -> bool:
        return timezone.now() <= self.expired_time

    @property
    def plugin_claims(self) -> dict[str, Any]:
        return {
            key: val
            for plugin in (self.plugins or {})
            for key, val in plugin_manager.get_extra_claims(
                self, plugin
            ).items()
        }

    @property
    def registered_claims(self) -> dict:
        claims = self.extra_claims.copy() if self.extra_claims else {}
        claims.update(self.plugin_claims)

        # registered claims
        if sub := self.subject:
            claims[jwt_settings.SUBJECT_CLAIM] = sub
        if aud := self.audience:
            claims[jwt_settings.AUDIENCE_CLAIM] = aud
        if nbf := self.not_before:
            claims[jwt_settings.NOT_BEFORE_CLAIM] = datetime_to_epoch(nbf)

        return claims

    @property
    def refresh_token_claims(self) -> dict:
        claims = self.registered_claims
        claims[
            jwt_settings.EXPIRATION_CLAIM
        ] = datetime_to_epoch(self.expired_time)
        claims[
            jwt_settings.ISSUED_AT_CLAIM
        ] = datetime_to_epoch(self.issued_at)
        claims[
            jwt_auth_settings.AUTHN_REFRESH_TOKEN_ID_CLAIM
        ] = self.pk
        claims[jwt_auth_settings.AUTHN_SESSION_ID_CLAIM] = self.session_id
        return claims

    @property
    def access_token_claims(self) -> dict:
        claims = self.registered_claims

        # multi factor claims
        claims[
            jwt_auth_settings.AUTHN_MULTI_FACTOR_AUTH_CLAIM
        ] = self.multi_factor_auth
        if mfe := self.multi_factor_expires:
            claims[
                jwt_auth_settings.AUTHN_MULTI_FACTOR_EXPIRATION_CLAIM
            ] = datetime_to_epoch(mfe)
        if mfr := self.multi_factor_ref:
            claims[
                jwt_auth_settings.AUTHN_MULTI_FACTOR_REFERENCE_CLAIM
            ] = mfr

        claims[
            jwt_auth_settings.AUTHN_REFRESH_TOKEN_ID_CLAIM
        ] = self.pk
        claims[jwt_auth_settings.AUTHN_SESSION_ID_CLAIM] = self.session_id

        return claims

    def get_access_jwt(
            self, *,
            override_claims: dict = None,
            current_time: datetime.datetime = None,
    ) -> AccessTokenObject:
        claims = self.access_token_claims
        if override_claims:
            claims.update(override_claims)
        return jwt_auth_settings.ACCESS_TOKEN_CLASS(
            payload=claims, current_time=current_time)

    def get_refresh_jwt(
            self, *,
            override_claims: dict = None,
            current_time: datetime.datetime = None,
    ) -> RefreshTokenObject:
        claims = self.refresh_token_claims
        if override_claims:
            claims.update(override_claims)
        return jwt_auth_settings.REFRESH_TOKEN_CLASS(
            payload=claims, current_time=current_time)

    def update_multi_factor(
            self, reference: str, *,
            current_time: datetime.datetime = None,
            lifetime: datetime.timedelta = None,
            save: bool = True):
        if current_time is None:
            current_time = timezone.now()
        if lifetime is None:
            lifetime = jwt_auth_settings.AUTHN_MULTI_FACTOR_SESSION_LIFETIME
        self.multi_factor_auth = True
        self.multi_factor_ref = reference
        self.multi_factor_expires = current_time + lifetime
        if save:
            self.save(update_fields=[
                "multi_factor_auth",
                "multi_factor_ref",
                "multi_factor_expires"
            ])

    def set_plugin(self, name: str, **kwargs) -> RefreshTokenPluginBase:
        result = plugin_manager.set_plugin_object(
            self, name, **kwargs)
        if not self.plugins:
            self.plugins = [name]
        elif name in self.plugins:
            return result
        self.plugins.append(name)
        self.save(update_fields=["plugins"])
        return result
