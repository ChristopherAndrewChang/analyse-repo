from __future__ import annotations
from typing import TYPE_CHECKING

import hashlib
import hmac
import logging

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

from django.db import models
from django.db.models.manager import BaseManager
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from idvalid_core.models import get_subid_model

from authn_sdk.constants import (
    PLATFORM_TYPE_MOBILE,
    PLATFORM_TYPE_DESKTOP,
    PLATFORM_TYPE_WEB,
    PLATFORM_TYPE_OTHER,
)

from authn.generators import generate_rsa_private_key, generate_bytes
from authn.settings import authn_settings

if TYPE_CHECKING:
    from .totp_device import TOTPDevice


logger = logging.getLogger(__name__)
__all__ = (
    "PlatformQuerySet",
    "PlatformManager",
    "Platform",
)


def generate_private_key_der() -> bytes:
    private_key = generate_rsa_private_key()
    enc_alg = (
        serialization.NoEncryption()
        if authn_settings.PLATFORM_PRIVATE_KEY_SECRET is None else
        serialization.BestAvailableEncryption(
            authn_settings.PLATFORM_PRIVATE_KEY_SECRET.encode()
        )
    )
    return private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=enc_alg)


def generate_salt() -> bytes:
    return generate_bytes(20)


def load_private_key_der(data: bytes):
    return serialization.load_der_private_key(
        data,
        password=authn_settings.PLATFORM_PRIVATE_KEY_SECRET,
        backend=default_backend()
    )


class PlatformQuerySet(models.QuerySet):
    def get_encrypted(self, enc_subid: str, salt: str) -> Platform:
        pass


_PlatformManagerBase = models.Manager.from_queryset(
    PlatformQuerySet
)  # type: type[PlatformQuerySet]


class PlatformManager(_PlatformManagerBase, BaseManager):
    pass


class Platform(get_subid_model()):
    MOBILE_PLATFORM = PLATFORM_TYPE_MOBILE
    DESKTOP_PLATFORM = PLATFORM_TYPE_DESKTOP
    WEB_PLATFORM = PLATFORM_TYPE_WEB
    OTHER_PLATFORM = PLATFORM_TYPE_OTHER
    PLATFORM_TYPES = (
        (MOBILE_PLATFORM, "Mobile"),
        (DESKTOP_PLATFORM, "Desktop"),
        (WEB_PLATFORM, "Web"),
        (OTHER_PLATFORM, "Other"),
    )

    totp_device_id: int
    totp_device = models.ForeignKey(
        "authn.TOTPDevice", on_delete=models.CASCADE,
        related_name="platforms",
        verbose_name=_("totp device")
    )  # type: TOTPDevice
    private_key_der = models.BinaryField(
        _("private key der"),
        default=generate_private_key_der
    )  # type: bytes
    salt = models.BinaryField(
        _("salt"),
        default=generate_salt)  # type: bytes

    name = models.CharField(
        _("name"), max_length=150)
    platform_type = models.CharField(
        _("platform type"),
        choices=PLATFORM_TYPES,
        default=WEB_PLATFORM,
        max_length=32)

    is_deleted = models.BooleanField(
        _("deleted flag"),
        default=False, editable=False)
    deleted_time = models.DateTimeField(
        _("deleted time"),
        null=True, blank=True, editable=False)

    objects = PlatformManager()

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.deleted_time = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_time"])

    def delete_from_db(self, *args, **kwargs):
        return super().delete(*args, **kwargs)

    @cached_property
    def private_key(self):
        return load_private_key_der(self.private_key_der)

    @cached_property
    def public_key(self):
        return self.private_key.public_key()

    def decrypt(self, ciphertext: bytes, label: bytes = None) -> bytes:
        return self.private_key.decrypt(
            ciphertext,
            padding=padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=hmac.new(self.salt, label, hashlib.sha256).digest()
            )
        )

    def is_mobile(self) -> bool:
        return self.platform_type == self.MOBILE_PLATFORM
