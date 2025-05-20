from __future__ import annotations
from typing import TYPE_CHECKING

import logging
import secrets
import base64

# from webauthn.helpers.structs import (
#     PublicKeyCredentialRpEntity,
#     PublicKeyCredentialUserEntity,
#     PublicKeyCredentialParameters,
#     AttestationConveyancePreference,
#     AuthenticatorSelectionCriteria,
#     ResidentKeyRequirement,
#     UserVerificationRequirement,
#     PublicKeyCredentialCreationOptions,
# )
from webauthn import (
    verify_registration_response,
    verify_authentication_response,
)
from webauthn.helpers import (
    parse_registration_credential_json,
    parse_authentication_credential_json,
)
from webauthn.helpers.exceptions import WebAuthnException
from webauthn.helpers.structs import (
    RegistrationCredential,
    AuthenticationCredential,
)

from django.db import models
from django.db.models.manager import BaseManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from idvalid_core.models import get_subid_model

from authn.settings import authn_settings

if TYPE_CHECKING:
    from typing import Any, Self

    from webauthn.registration.verify_registration_response import (
        VerifiedRegistration,
    )
    from webauthn.authentication.verify_authentication_response import (
        VerifiedAuthentication,
    )

    from authn.models import User


logger = logging.getLogger(__name__)
__all__ = (
    "PasskeyQuerySet",
    "PasskeyManager",
    "Passkey",

    "PasskeyChallengeQuerySet",
    "PasskeyChallengeManager",
    "PasskeyChallenge",
)


class InvalidCredentialId(WebAuthnException):
    pass


class InvalidUserException(WebAuthnException):
    pass


class DisabledPasskeyException(WebAuthnException):
    pass


class AlreadyRegisteredException(WebAuthnException):
    pass


class PasskeyQuerySet(models.QuerySet):
    def active(self, *args, **kwargs) -> Self:
        return self.filter(*args, is_active=True, **kwargs)


_PasskeyManagerBase = models.Manager.from_queryset(
    PasskeyQuerySet
)  # type: type[PasskeyQuerySet]


class PasskeyManager(_PasskeyManagerBase, BaseManager):
    pass


class Passkey(get_subid_model()):
    user_id: int
    user = models.ForeignKey(
        "authn.User", on_delete=models.CASCADE,
        related_name="passkeys")  # type: User
    is_active = models.BooleanField(
        _("active flag"), default=True)

    credential_id = models.BinaryField(
        _("credential_id"),
        db_index=True, unique=True)
    public_key = models.BinaryField(
        _("public key"))  # type: bytes
    sign_count = models.PositiveIntegerField(
        _("sign count"))  # type: int
    attestation_object = models.BinaryField(
        _("attestation object"))  # type: bytes
    aaguid = models.CharField(
        _("aaguid"), max_length=36)

    last_used_at = models.DateTimeField(
        _("last used at"), null=True, blank=True)
    created_at = models.DateTimeField(
        _("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(
        _("updated at"), auto_now=True)

    objects = PasskeyManager()

    def renew(self, verified: VerifiedRegistration):
        self.public_key = verified.credential_public_key
        self.sign_count = verified.sign_count
        self.attestation_object = verified.attestation_object
        self.aaguid = verified.aaguid
        self.last_used_at = None
        self.save(update_fields=[
            "public_key",
            "sign_count",
            "attestation_object",
            "aaguid",
            "last_used_at",
        ])

    def update_sign_count(self, value):
        self.sign_count = value
        self.save(update_fields=["sign_count"])

    def auth_passed(self, verified: VerifiedAuthentication):
        self.sign_count = verified.new_sign_count
        self.last_used_at = timezone.now()
        self.save(update_fields=["sign_count", "last_used_at"])


def bytes_to_base64url(val: bytes) -> str:
    """
    Base64URL-encode the provided bytes
    """
    return base64.urlsafe_b64encode(val).decode("utf-8").rstrip("=")


def generate_challenge(length: int = 64) -> bytes:
    return secrets.token_bytes(length)


class PasskeyChallengeQuerySet(models.QuerySet):
    def for_registration(self, *args, **kwargs) -> Self:
        return self.filter(
            *args,
            usage=PasskeyChallenge.REGISTRATION_USAGE,
            **kwargs)

    def for_authentication(self, *args, **kwargs) -> Self:
        return self.filter(
            *args,
            usage=PasskeyChallenge.AUTHENTICATION_USAGE,
            **kwargs)


_PasskeyChallengeManagerBase = models.Manager.from_queryset(
    PasskeyChallengeQuerySet
)  # type: type[PasskeyChallengeQuerySet]


class PasskeyChallengeManager(_PasskeyChallengeManagerBase, BaseManager):
    def create_registration(self, **kwargs) -> PasskeyChallenge:
        kwargs["usage"] = PasskeyChallenge.REGISTRATION_USAGE
        return self.create(**kwargs)

    def create_authentication(self, **kwargs) -> PasskeyChallenge:
        kwargs["usage"] = PasskeyChallenge.AUTHENTICATION_USAGE
        return self.create(**kwargs)


class PasskeyChallenge(get_subid_model()):
    REGISTRATION_USAGE = "registration"
    AUTHENTICATION_USAGE = "authentication"
    USAGE_CHOICES = (
        (REGISTRATION_USAGE, "Registration"),
        (AUTHENTICATION_USAGE, "Authentication"),
    )
    user_id: int
    user = models.ForeignKey(
        "authn.User", on_delete=models.CASCADE,
        related_name="passkey_challenges",
        null=True, blank=True)  # type: User | None
    challenge = models.BinaryField(
        _("challenge"), max_length=64,
        default=generate_challenge
    )  # type: bytes
    # timeout = models.PositiveIntegerField(
    #     _("timeout"), null=True, blank=True)
    usage = models.CharField(
        _("usage"), max_length=64,
        choices=USAGE_CHOICES)

    # passkey_id: int
    # passkey = models.ForeignKey(
    #     "authn.Passkey", on_delete=models.SET_NULL,
    #     related_name="challenges",
    #     null=True, blank=True
    # )  # type: Passkey

    created_at = models.DateTimeField(
        _("created at"), auto_now_add=True)

    objects = PasskeyChallengeManager()

    def get_registration_options(self):
        user = self.user
        return {
            "rp": {
                "name": authn_settings.PASSKEY_RP_NAME,
                "id": authn_settings.PASSKEY_RP_ID,
            },
            "user": {
                "id": user.subid,
                "name": user.email or user.phone,
                "displayName": user.name,
            },
            "challenge": bytes_to_base64url(self.challenge),
            "pubKeyCredParams": [
                {"type": "public-key", "alg": alg}
                for alg in authn_settings.PASSKEY_SUPPORTED_ALGORITHMS
            ],
            "timeout": authn_settings.PASSKEY_DEFAULT_TIMEOUT,
            "authenticatorSelection": {
                "residentKey": "required",
                "requireResidentKey": True,
                "userVerification": "required",
            },
            "attestation": "none",
            "excludeCredentials": [
                {
                    "id": bytes_to_base64url(passkey.credential_id),
                    "type": "public-key",
                }
                for passkey in user.passkeys.active()
            ],
            "hints": [],
            "extensions": {
                "credProps": True
            },
        }

    def get_authentication_options(self):
        allow_creds = []
        config = {
            "rpId": authn_settings.PASSKEY_RP_ID,
            "challenge": bytes_to_base64url(self.challenge),
            "timeout": authn_settings.PASSKEY_DEFAULT_TIMEOUT,
            "userVerification": "required",
            "allowCredentials": allow_creds
        }

        if user := self.user:
            for item in user.passkeys.filter(is_active=True):
                allow_creds.append({
                    "id": bytes_to_base64url(item.credential_id),
                    "type": "public-key",
                    "transports": [],
                })

        return config

    def get_options(self):
        if self.usage == self.REGISTRATION_USAGE:
            return self.get_registration_options()
        elif self.usage == self.AUTHENTICATION_USAGE:
            return self.get_authentication_options()

    def verify_registration(
            self, credential: str | dict | RegistrationCredential
    ) -> Passkey:
        if not (user_id := self.user_id):
            raise TypeError("user_id is none")

        if not isinstance(credential, RegistrationCredential):
            credential = parse_registration_credential_json(credential)

        verified = verify_registration_response(
            credential=credential,
            expected_challenge=self.challenge,
            expected_rp_id=authn_settings.PASSKEY_RP_ID,
            expected_origin=authn_settings.PASSKEY_ALLOWED_ORIGIN,
            require_user_verification=True,
            supported_pub_key_algs=authn_settings.PASSKEY_SUPPORTED_ALGORITHMS)

        passkey, created = Passkey.objects.get_or_create(
            credential_id=verified.credential_id,
            defaults={
                "public_key": verified.credential_public_key,
                "sign_count": verified.sign_count,
                "attestation_object": verified.attestation_object,
                "aaguid": verified.aaguid,
                "user_id": user_id,
            }
        )  # type: Passkey, bool
        if not created:
            if passkey.user_id != user_id:
                raise AlreadyRegisteredException(
                    "id already registered")
            passkey.renew(verified)

        return passkey

    def verify_authentication(
            self, credential: str | dict | AuthenticationCredential
    ) -> Passkey:
        if not isinstance(credential, AuthenticationCredential):
            credential = parse_authentication_credential_json(credential)
        try:
            passkey = Passkey.objects.get(credential_id=credential.raw_id)
        except Passkey.DoesNotExist:
            raise InvalidCredentialId("Unrecognized id")
        if not passkey.is_active:
            raise DisabledPasskeyException("Passkey disabled")
        if (user_id := self.user_id) and user_id != passkey.user_id:
            raise InvalidUserException("User does not match")

        verified = verify_authentication_response(
            credential=credential,
            expected_challenge=self.challenge,
            expected_rp_id=authn_settings.PASSKEY_RP_ID,
            expected_origin=authn_settings.PASSKEY_ALLOWED_ORIGIN,
            credential_public_key=passkey.public_key,
            credential_current_sign_count=passkey.sign_count,
            require_user_verification=True)
        passkey.auth_passed(verified)
        return passkey

    def verify(
            self,
            credential: str | dict,
    ) -> Passkey:
        if (usage := self.usage) == self.REGISTRATION_USAGE:
            result = self.verify_registration(credential)
        elif usage == self.AUTHENTICATION_USAGE:
            result = self.verify_authentication(credential)
        else:
            raise TypeError(f"Unknown usage: {usage}")
        self.delete()
        return result
