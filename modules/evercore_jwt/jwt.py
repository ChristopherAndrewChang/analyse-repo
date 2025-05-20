from __future__ import annotations
from typing import TYPE_CHECKING

import json

from calendar import timegm
from collections.abc import Iterable, Sequence
from datetime import datetime, timedelta, timezone

from jwt import api_jws
from jwt.api_jwt import PyJWT
from jwt.exceptions import (
    MissingRequiredClaimError,
    ImmatureSignatureError,
    ExpiredSignatureError,
    InvalidIssuedAtError,
    InvalidJTIError,
    InvalidSubjectError,
    InvalidIssuerError,
    InvalidAudienceError,
)

from .exceptions import (
    InvalidNotBeforeError,
    InvalidExpirationError,
    InvalidTokenTypeError,
)
from .settings import jwt_settings

if TYPE_CHECKING:
    from typing import Any
    from jwt.algorithms import AllowedPrivateKeys, AllowedPublicKeys
    from jwt.api_jwk import PyJWK


VERIFY_SIGNATURE = "verify_signature"
VERIFY_EXP = "verify_exp"
VERIFY_NBF = "verify_nbf"
VERIFY_IAT = "verify_iat"
VERIFY_AUD = "verify_aud"
VERIFY_ISS = "verify_iss"
VERIFY_SUB = "verify_sub"
VERIFY_JTI = "verify_jti"
VERIFY_TTY = "verify_tty"
REQUIRED_FIELDS = "require"


class JWT(PyJWT):
    def __init__(
            self, options: dict[str, Any] | None = None, *,
            strict: bool = False):
        super().__init__(options)
        self.strict = strict

    @staticmethod
    def _get_default_options() -> dict[str, bool | list[str]]:
        return {
            VERIFY_SIGNATURE: True,
            VERIFY_EXP: True,
            VERIFY_NBF: True,
            VERIFY_IAT: True,
            VERIFY_AUD: True,
            VERIFY_ISS: True,
            VERIFY_SUB: True,
            VERIFY_JTI: True,
            VERIFY_TTY: True,
            REQUIRED_FIELDS: [],
        }

    def encode(
        self,
        payload: dict[str, Any],
        key: AllowedPrivateKeys | PyJWK | str | bytes,
        algorithm: str | None = None,
        headers: dict[str, Any] | None = None,
        json_encoder: type[json.JSONEncoder] | None = None,
        sort_headers: bool = True,
        time_claims: list[str] = None,
    ) -> str:
        # Check that we get a dict
        if not isinstance(payload, dict):
            raise TypeError(
                "Expecting a dict object, as JWT only supports "
                "JSON objects as payloads."
            )

        registered_time_claims = {
            jwt_settings.EXPIRATION_CLAIM,
            jwt_settings.ISSUED_AT_CLAIM,
            jwt_settings.NOT_BEFORE_CLAIM
        }
        if time_claims:
            registered_time_claims.update(time_claims)

        payload = payload.copy()
        for time_claim in registered_time_claims:
            if isinstance((claim := payload.get(time_claim)), datetime):
                payload[time_claim] = timegm(claim.utctimetuple())

        json_payload = self._encode_payload(
            payload,
            headers=headers,
            json_encoder=json_encoder)

        return api_jws.encode(
            json_payload,
            key,
            algorithm,
            headers,
            json_encoder,
            sort_headers=sort_headers)

    def decode_complete(
        self,
        jwt: str | bytes,
        key: AllowedPublicKeys | PyJWK | str | bytes = "",
        algorithms: Sequence[str] | None = None,
        options: dict[str, Any] | None = None,
        # could be used as passthrough to api_jws, consider removal in pyjwt3
        detached_payload: bytes | None = None,
        # passthrough arguments to _validate_claims
        # consider putting in options
        audience: str | Iterable[str] | None = None,
        issuer: str | Sequence[str] | None = None,
        subject: str | None = None,
        token_type: str | None = None,
        leeway: float | timedelta = 0,
        now: datetime | None = None,
        # kwargs
        **kwargs: Any,
    ) -> dict[str, Any]:
        options = dict(options or {})  # shallow-copy or initialize an empty dict
        options.setdefault(VERIFY_SIGNATURE, True)

        if not options[VERIFY_SIGNATURE]:
            options.setdefault(VERIFY_EXP, False)
            options.setdefault(VERIFY_NBF, False)
            options.setdefault(VERIFY_IAT, False)
            options.setdefault(VERIFY_AUD, False)
            options.setdefault(VERIFY_ISS, False)
            options.setdefault(VERIFY_SUB, False)
            options.setdefault(VERIFY_JTI, False)
            options.setdefault(VERIFY_TTY, False)

        decoded = api_jws.decode_complete(
            jwt,
            key=key,
            algorithms=algorithms,
            options=options,
            detached_payload=detached_payload,
        )

        payload = self._decode_payload(decoded)

        merged_options = {**self.options, **options}
        self._validate_claims(
            payload,
            merged_options,
            audience=audience,
            issuer=issuer,
            subject=subject,
            token_type=token_type,
            leeway=leeway,
            now=now,
        )

        decoded["payload"] = payload
        return decoded

    def decode(
        self,
        jwt: str | bytes,
        key: AllowedPublicKeys | PyJWK | str | bytes = "",
        algorithms: Sequence[str] | None = None,
        options: dict[str, Any] | None = None,
        # deprecated arg, remove in pyjwt3
        verify: bool | None = None,
        # could be used as passthrough to api_jws, consider removal in pyjwt3
        detached_payload: bytes | None = None,
        # passthrough arguments to _validate_claims
        # consider putting in options
        audience: str | Iterable[str] | None = None,
        subject: str | None = None,
        issuer: str | Sequence[str] | None = None,
        token_type: str | None = None,
        leeway: float | timedelta = 0,
        now: datetime | None = None,
        # kwargs
        **kwargs: Any,
    ) -> Any:
        decoded = self.decode_complete(
            jwt,
            key,
            algorithms,
            options,
            verify=verify,
            detached_payload=detached_payload,
            audience=audience,
            subject=subject,
            issuer=issuer,
            token_type=token_type,
            leeway=leeway,
            now=now,
        )
        return decoded["payload"]

    def _validate_claims(
        self,
        payload: dict[str, Any],
        options: dict[str, Any],
        audience=None,
        issuer=None,
        subject: str | None = None,
        token_type: str | None = None,
        leeway: float | timedelta = 0,
        now: datetime | None = None
    ) -> None:
        if isinstance(leeway, timedelta):
            leeway = leeway.total_seconds()

        if now is None:
            now = datetime.now(tz=timezone.utc).timestamp()
        else:
            if not isinstance(now, datetime):
                ValueError("now must be an instance of datetime")
            now = now.astimezone(timezone.utc).timestamp()

        if audience is not None and not isinstance(audience, (str, Iterable)):
            raise TypeError("audience must be a string, iterable or None")

        self._validate_required_claims(payload, options)

        if options[VERIFY_IAT]:
            self._validate_iat(payload, now, leeway)
        if options[VERIFY_NBF]:
            self._validate_nbf(payload, now, leeway)
        if options[VERIFY_EXP]:
            self._validate_exp(payload, now, leeway)
        if options[VERIFY_ISS]:
            self._validate_iss(payload, issuer)
        if options[VERIFY_AUD]:
            self._validate_aud(
                payload, audience, strict=options.get("strict_aud", False))
        if options[VERIFY_SUB]:
            self._validate_sub(payload, subject)
        if options[VERIFY_JTI]:
            self._validate_jti(payload)
        if options[VERIFY_TTY]:
            self._validate_tty(payload, token_type)

    def _validate_iat(
        self,
        payload: dict[str, Any],
        now: float,
        leeway: float,
    ) -> None:
        claim = jwt_settings.ISSUED_AT_CLAIM
        try:
            claimed = int(payload[claim])
        except KeyError:
            # allow unspecified iat
            return
        except ValueError:
            raise InvalidIssuedAtError(
                f"Issued At claim ({claim}) must be an integer."
            ) from None

        if claimed > (now + leeway):
            raise ImmatureSignatureError(
                f"The token is not yet valid ({claim})")

    def _validate_nbf(
        self,
        payload: dict[str, Any],
        now: float,
        leeway: float,
    ) -> None:
        claim = jwt_settings.NOT_BEFORE_CLAIM
        try:
            claimed = int(payload[claim])
        except KeyError:
            # allow unspecified nbf
            return
        except ValueError:
            raise InvalidNotBeforeError(
                f"Not Before claim ({claim}) must be an integer.") from None

        if claimed > (now + leeway):
            raise ImmatureSignatureError(
                f"The token is not yet valid ({claim})")

    def _validate_exp(
        self,
        payload: dict[str, Any],
        now: float,
        leeway: float,
    ) -> None:
        claim = jwt_settings.EXPIRATION_CLAIM
        try:
            claimed = int(payload[claim])
        except KeyError:
            raise MissingRequiredClaimError(claim)
        except ValueError:
            raise InvalidExpirationError(
                f"Expiration Time claim ({claim}) must be an integer."
            ) from None

        if claimed <= (now - leeway):
            raise ExpiredSignatureError("Signature has expired")

    def _validate_jti(self, payload: dict[str, Any]) -> None:
        """
        Checks whether "jti" if in the payload is valid ot not
        This is an Optional claim

        :param payload(dict): The payload which needs to be validated
        """
        claim = jwt_settings.TOKEN_ID_CLAIM
        try:
            claimed = payload[claim]
        except KeyError:
            raise MissingRequiredClaimError(claim)

        if not isinstance(claimed, str):
            raise InvalidJTIError(f"JWT ID claim ({claim}) must be a string")

    def _validate_sub(self, payload: dict[str, Any], subject=None) -> None:
        """
        Checks whether "sub" if in the payload is valid ot not.
        This is an Optional claim

        :param payload(dict): The payload which needs to be validated
        :param subject(str): The subject of the token
        """
        claim = jwt_settings.SUBJECT_CLAIM
        try:
            claimed = payload[claim]
        except KeyError:
            raise MissingRequiredClaimError(claim)

        if subject is None:
            return

        if not isinstance(claimed, str):
            raise InvalidSubjectError(
                f"Subject claim ({claim}) must be a string")
        if claimed != subject:
            raise InvalidSubjectError(
                "Invalid subject")

    def _validate_iss(self, payload: dict[str, Any], issuer: Any) -> None:
        claim = jwt_settings.ISSUER_CLAIM
        try:
            claimed = payload[claim]
        except KeyError:
            raise MissingRequiredClaimError(claim)

        if issuer is None:
            return

        if isinstance(issuer, str):
            if claimed != issuer:
                raise InvalidIssuerError(
                    "Invalid issuer")
        else:
            if claimed not in issuer:
                raise InvalidIssuerError("Invalid issuer")

    def _validate_tty(self, payload: dict[str, Any], token_type: Any) -> None:
        claim = jwt_settings.TOKEN_TYPE_CLAIM
        try:
            claimed = payload[claim]
        except KeyError:
            raise MissingRequiredClaimError(claim)

        if token_type is None:
            return

        if not isinstance(claimed, str):
            raise InvalidTokenTypeError(
                f"Token type claim ({claim}) must be a string")
        if claimed != token_type:
            raise InvalidTokenTypeError(
                "Invalid token type")

    def _validate_aud(
        self,
        payload: dict[str, Any],
        audience: str | Iterable[str] | None,
        *,
        strict: bool = False,
    ) -> None:
        claim = jwt_settings.AUDIENCE_CLAIM

        if audience is None:
            try:
                claimed = payload[claim]
            except KeyError:
                return
            if claimed:
                # Application did not specify an audience, but
                # the token has the audience claim
                raise InvalidAudienceError("Invalid audience")
            return

        try:
            claimed = payload[claim]
        except KeyError:
            # Application specified an audience, but it could not be
            # verified since the token does not contain a claim.
            raise MissingRequiredClaimError(claim)
        else:
            if not claimed:
                raise InvalidAudienceError("Invalid audience")

        # In strict mode, we forbid list matching: the supplied audience
        # must be a string, and it must exactly match the audience claim.
        if strict:
            # Only a single audience is allowed in strict mode.
            if not isinstance(audience, str):
                raise ValueError(
                    "Only single audience is allowed is strict mode")

            # Only a single audience claim is allowed in strict mode.
            if not isinstance(claimed, str):
                raise InvalidAudienceError(
                    f"Invalid audience claim ({claim}) format in token (strict)")

            if audience != claimed:
                raise InvalidAudienceError(
                    f"Audience claim ({claim}) doesn't match (strict)")
            return

        if isinstance(claimed, str):
            claimed = [claimed]
        if (
                not isinstance(claimed, list) or
                any(not isinstance(c, str) for c in claimed)
        ):
            raise InvalidAudienceError(
                f"Invalid audience claim ({claim}) format in token")

        if isinstance(audience, str):
            audience = [audience]

        if all(aud not in claimed for aud in audience):
            raise InvalidAudienceError(
                f"Audience claim ({claim}) doesn't match")


_jwt_global_obj = JWT()
encode = _jwt_global_obj.encode
decode_complete = _jwt_global_obj.decode_complete
decode = _jwt_global_obj.decode
