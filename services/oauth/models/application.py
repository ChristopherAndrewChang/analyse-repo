from __future__ import annotations
from typing import TYPE_CHECKING

import logging
import os

import requests

from urllib.parse import urlencode

from jwcrypto import jwk
from jwcrypto.common import base64url_encode

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models.manager import BaseManager
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from oauth2_provider.models import AbstractApplication, ApplicationManager
from oauth2_provider.settings import oauth2_settings
from oauth2_provider.utils import jwk_from_pem

from .base import TemporaryUser

if TYPE_CHECKING:
    from typing import Self


logger = logging.getLogger(__name__)
__all__ = (
    "ApplicationQuerySet",
    "ApplicationManager",
    "Application",
)


class ApplicationQuerySet(models.QuerySet):
    def active(self, *args, **kwargs) -> Self:
        return self.filter(*args, is_active=True, **kwargs)


_ApplicationManagerBase = ApplicationManager.from_queryset(
    ApplicationQuerySet
)  # type: type[ApplicationQuerySet]


class ApplicationManager(
        _ApplicationManagerBase, ApplicationManager, BaseManager):
    pass


class Application(TemporaryUser, AbstractApplication):
    user_id = models.PositiveBigIntegerField(
        _("user id"))

    is_active = models.BooleanField(
        _("active flag"), default=True)
    prompt_callback_url = models.URLField(
        _("prompt callback url"),
        null=True, blank=True)

    objects = ApplicationManager()

    def natural_key(self):
        return (self.client_id,)

    def get_absolute_url(self):
        return reverse("oauth_management:detail", args=[str(self.pk)])

    @property
    def jwk_key(self):
        if self.algorithm == AbstractApplication.RS256_ALGORITHM:
            if not (rsa_private_key := oauth2_settings.OIDC_RSA_PRIVATE_KEY):
                raise ImproperlyConfigured("You must set OIDC_RSA_PRIVATE_KEY to use RSA algorithm")
            if os.path.exists(rsa_private_key):
                with open(rsa_private_key, "r") as fp:
                    rsa_private_key = fp.read()
            return jwk_from_pem(rsa_private_key)
        elif self.algorithm == AbstractApplication.HS256_ALGORITHM:
            return jwk.JWK(kty="oct", k=base64url_encode(self.client_secret))
        raise ImproperlyConfigured("This application does not support signed tokens")

    def call_prompt_callback(self, data: dict, timeout: float = 2):
        if not (url := self.prompt_callback_url):
            raise TypeError("has no callback url")
        params = urlencode(data)
        url = (
            f"{url}&{params}"
            if "?" in url else
            f"{url}?{params}"
        )
        return requests.get(url, timeout=timeout)
