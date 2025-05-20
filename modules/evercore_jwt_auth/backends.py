from __future__ import annotations
from typing import TYPE_CHECKING

from jwt import (
    algorithms,
    InvalidAlgorithmError,
    InvalidTokenError,
)
from evercore_jwt.jwt import (
    encode as jwt_encode,
    decode as jwt_decode,
    VERIFY_AUD,
    VERIFY_SIGNATURE,
    REQUIRED_FIELDS,
)

from django.utils.translation import gettext_lazy as _

from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.exceptions import TokenBackendError

from evercore_jwt.settings import jwt_settings

from .utils import format_lazy

if TYPE_CHECKING:
    from typing import Dict, Any, Sequence
    from datetime import datetime
    from .tokens import Token


ALLOWED_ALGORITHMS = {
    "HS256",
    "HS384",
    "HS512",
    "RS256",
    "RS384",
    "RS512",
    "ES256",
    "ES384",
    "ES512",
}


class EvercoreJWTBackend(TokenBackend):
    def _validate_algorithm(self, algorithm: str) -> None:
        """
        Ensure that the nominated algorithm is recognized, and that cryptography is installed for those
        algorithms that require it
        """
        if algorithm not in ALLOWED_ALGORITHMS:
            raise TokenBackendError(
                format_lazy(_("Unrecognized algorithm type '{}'"), algorithm)
            )

        if algorithm in algorithms.requires_cryptography and not algorithms.has_crypto:
            raise TokenBackendError(
                format_lazy(
                    _("You must have cryptography installed to use {}."), algorithm
                )
            )

    def encode(
            self, payload: Dict[str, Any], *,
            time_claims: Sequence[str] = None) -> str:
        """
        Returns an encoded token for the given payload dictionary.
        """
        jwt_payload = payload.copy()
        if self.issuer is not None:
            jwt_payload[jwt_settings.ISSUER_CLAIM] = self.issuer
        if aud_claim := jwt_settings.AUDIENCE_CLAIM:
            if (
                    (aud := self.audience) is not None and
                    aud_claim not in jwt_payload
            ):
                jwt_payload[aud_claim] = aud

        token = jwt_encode(
            jwt_payload,
            self.signing_key,
            algorithm=self.algorithm,
            json_encoder=self.json_encoder,
            time_claims=time_claims,
        )
        if isinstance(token, bytes):
            # For PyJWT <= 1.7.1
            return token.decode("utf-8")
        # For PyJWT >= 2.0.0a1
        return token

    def decode(
            self, token: Token,
            verify: bool = True,
            token_type: str = None,
            require: Sequence[str] = None,
            now: datetime = None) -> Dict[str, Any]:
        """
        Performs a validation of the given token and returns its payload
        dictionary.

        Raises a `TokenBackendError` if the token is malformed, if its
        signature check fails, or if its 'exp' claim indicates it has expired.
        """
        options = {
            VERIFY_AUD: self.audience is not None,
            VERIFY_SIGNATURE: verify,
        }
        if require:
            options[REQUIRED_FIELDS] = require

        try:
            return jwt_decode(
                token,
                # verify params
                self.get_verifying_key(token),
                algorithms=[self.algorithm],
                # validation params
                audience=self.audience,
                issuer=self.issuer,
                token_type=token_type,
                leeway=self.get_leeway(),
                now=now,
                # opts
                options=options,
            )
        except InvalidAlgorithmError as ex:
            raise TokenBackendError(_("Invalid algorithm specified")) from ex
        except InvalidTokenError as ex:
            raise TokenBackendError(_("Token is invalid or expired")) from ex
