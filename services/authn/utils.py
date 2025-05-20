from __future__ import annotations
from typing import TYPE_CHECKING

import base64

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

from django.utils.functional import cached_property

from authn.settings import authn_settings

if TYPE_CHECKING:
    from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes, PublicKeyTypes


def load_login_private_key(pem_path: str = None) -> PrivateKeyTypes:
    if pem_path is None:
        pem_path = authn_settings.LOGIN_PRIVATE_KEY_PEM
    with open(pem_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=authn_settings.LOGIN_PRIVATE_KEY_PASSPHRASE,
            backend=default_backend()
        )
    return private_key


class LoginKey:
    def __init__(self, pem_path: str = None):
        self.pem_path = pem_path

    @cached_property
    def private_key(self) -> PrivateKeyTypes:
        return load_login_private_key(self.pem_path)

    @cached_property
    def public_key(self) -> PublicKeyTypes:
        return self.private_key.public_key()

    def decrypt(self, ciphertext: bytes, label: bytes) -> bytes:
        return self.private_key.decrypt(
            ciphertext,
            padding=padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=label
            )
        )


login_key = LoginKey()


def b64decode(
        value: str | bytes, *,
        strict: bool = True, urlsafe: bool = False):
    if mod := (len(value) % 4):
        if isinstance(value, bytes):
            value += b"=" * (4 - mod)
        else:
            value += "=" * (4 - mod)
    return base64.b64decode(
        value, altchars=(b'-_' if urlsafe else None), validate=strict)


def b64encode(value: bytes, *, remove_padding: bool = False, urlsafe: bool = False) -> bytes:
    result = base64.b64encode(value, altchars=(b'-_' if urlsafe else None))
    if remove_padding:
        return result.rstrip(b"=")
    return result
