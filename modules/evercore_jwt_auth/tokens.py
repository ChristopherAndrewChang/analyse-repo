from __future__ import annotations
from typing import TYPE_CHECKING

from datetime import datetime, timedelta
from uuid import uuid4

from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

from rest_framework_simplejwt.exceptions import TokenBackendError, TokenError

from evercore_jwt.settings import jwt_settings
from authn_sdk.constants import PLATFORM_TYPE_MOBILE

from .settings import jwt_auth_settings
from .state import token_backend as default_backend
from .utils import (
    make_utc,
    aware_utcnow,
    datetime_from_epoch,
    datetime_to_epoch,
    format_lazy,
)

if TYPE_CHECKING:
    type Payload = Dict[str, str | int | None]
    from typing import Any, Dict, Optional
    from .backends import EvercoreJWTBackend


__all__ = (
    "Token",
    "AccessToken",
    "RefreshToken",
)


class Token:
    """
    A class which validates and wraps an existing JWT or can be used to build a
    new JWT.
    """
    payload: "Payload"

    _token_backend: "Optional[EvercoreJWTBackend]" = default_backend
    token_type: "Optional[str]" = None
    lifetime: "Optional[timedelta]" = None

    def __init__(
            self, token: "Optional[Token, str, bytes]" = None, verify: bool = True, *,
            payload: "Payload" = None, current_time: datetime = None) -> None:
        """
        !!!! IMPORTANT !!!! MUST raise a TokenError with a user-facing error
        message if the given token is invalid, expired, or otherwise not safe
        to use.
        """
        if self.token_type is None or self.lifetime is None:
            raise TokenError(_("Cannot create token with no type or lifetime"))

        self.token = token
        self.current_time = (
            make_utc(current_time)
            if current_time is not None else
            aware_utcnow()
        )

        # Set up token
        if token is not None:
            # An encoded token was provided
            token_backend = self.get_token_backend()

            # Decode token
            try:
                self.payload = token_backend.decode(
                    token, verify=verify,
                    token_type=self.token_type,
                    now=self.current_time,
                )
            except TokenBackendError as e:
                raise TokenError(_("Token is invalid or expired")) from e
        else:
            if payload:
                payload = payload.copy()
                payload[jwt_settings.TOKEN_TYPE_CLAIM] = self.token_type
                self.payload = payload
                if not self.has_expiration:
                    self.set_exp(from_time=self.current_time, lifetime=self.lifetime)
                if not self.has_issued_at:
                    self.set_iat(at_time=self.current_time)
            else:
                self.payload = {
                    jwt_settings.TOKEN_TYPE_CLAIM: self.token_type
                }
                # Set "exp" and "iat" claims with default value
                self.set_exp(from_time=self.current_time, lifetime=self.lifetime)
                self.set_iat(at_time=self.current_time)
            # Set "jti" claim
            self.set_jti()

    def __repr__(self) -> str:
        return repr(self.payload)

    def __getitem__(self, key: str):
        return self.payload[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.payload[key] = value

    def __delitem__(self, key: str) -> None:
        del self.payload[key]

    def __contains__(self, key: str) -> Any:
        return key in self.payload

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        return self.payload.get(key, default)

    def __str__(self) -> str:
        """
        Signs and returns a token as a base64 encoded string.
        """
        return self.get_token_backend().encode(self.payload)

    def _check_expiration(
            self, claim: str,
            now: datetime | None = None):
        if now is None:
            now = self.current_time
        try:
            claim_value = self.payload[claim]
        except KeyError:
            raise TokenError(format_lazy(_("Token has no '{}' claim"), claim))

        claim_time = datetime_from_epoch(claim_value)
        leeway = self.get_token_backend().get_leeway()
        if claim_time <= (now - leeway):
            raise TokenError(format_lazy(_("Token '{}' claim has expired"), claim))

    def _check_maturity(
            self, claim: str, *,
            now: datetime | None = None,
            skip_key_error: bool = False):
        if now is None:
            now = self.current_time
        try:
            claim_value = self.payload[claim]
        except KeyError:
            if skip_key_error:
                return
            raise TokenError(format_lazy(_("Token has no '{}' claim"), claim))

        claim_time = datetime_from_epoch(claim_value)
        leeway = self.get_token_backend().get_leeway()
        if claim_time > (now + leeway):
            raise TokenError(format_lazy(_("Token '{}' is not yet valid"), claim))

    def _set_claim(self, claim: str, value: Any):
        self.payload[claim] = value

    @property
    def is_expired(self) -> bool:
        try:
            self._check_expiration(jwt_settings.EXPIRATION_CLAIM)
        except TokenError:
            return False
        return True

    @property
    def multi_factor_session_alive(self) -> bool:
        try:
            if not self.multi_factor_auth:
                return False
            self._check_expiration(jwt_auth_settings.AUTHN_MULTI_FACTOR_EXPIRATION_CLAIM)
        except TokenError:
            return False
        return True

    @property
    def is_immature(self) -> bool:
        try:
            self._check_maturity(
                jwt_settings.ISSUED_AT_CLAIM,
                skip_key_error=True)
            self._check_maturity(
                jwt_settings.NOT_BEFORE_CLAIM,
                skip_key_error=True)
        except TokenError:
            return False
        return True

    @property
    def has_issuer(self) -> bool:
        return self.has_claim(jwt_settings.ISSUER_CLAIM)

    @property
    def issuer(self) -> Any:
        return self.get_claim(jwt_settings.ISSUER_CLAIM)

    @property
    def has_subject(self) -> bool:
        return self.has_claim(jwt_settings.SUBJECT_CLAIM)

    @property
    def subject(self) -> Any:
        return self.get_claim(jwt_settings.SUBJECT_CLAIM)

    @property
    def has_audience(self) -> bool:
        return self.has_claim(jwt_settings.AUDIENCE_CLAIM)

    @property
    def audience(self) -> Any:
        return self.get_claim(jwt_settings.AUDIENCE_CLAIM)

    @property
    def has_expiration(self) -> bool:
        return self.has_claim(jwt_settings.EXPIRATION_CLAIM)

    @property
    def expiration_time(self) -> datetime:
        return datetime_from_epoch(
            self.get_claim(jwt_settings.EXPIRATION_CLAIM))

    @property
    def has_not_before(self) -> bool:
        return self.has_claim(jwt_settings.NOT_BEFORE_CLAIM)

    @property
    def not_before(self) -> datetime:
        return datetime_from_epoch(
            self.get_claim(jwt_settings.NOT_BEFORE_CLAIM))

    @property
    def has_issued_at(self) -> bool:
        return self.has_claim(jwt_settings.ISSUED_AT_CLAIM)

    @property
    def issued_at(self) -> datetime:
        return datetime_from_epoch(
            self.get_claim(jwt_settings.ISSUED_AT_CLAIM))

    @property
    def has_jwt_id(self) -> bool:
        return self.has_claim(jwt_settings.TOKEN_ID_CLAIM)

    @property
    def jwt_id(self) -> Any:
        return self.get_claim(jwt_settings.TOKEN_ID_CLAIM)

    @property
    def has_multi_factor_auth(self) -> bool:
        return self.has_claim(
            jwt_auth_settings.AUTHN_MULTI_FACTOR_AUTH_CLAIM)

    @property
    def multi_factor_auth(self) -> Any:
        return self.get_claim(
            jwt_auth_settings.AUTHN_MULTI_FACTOR_AUTH_CLAIM)

    @property
    def has_multi_factor_expiration(self) -> bool:
        return self.has_claim(
            jwt_auth_settings.AUTHN_MULTI_FACTOR_EXPIRATION_CLAIM)

    @property
    def multi_factor_expiration(self) -> datetime:
        return datetime_from_epoch(
            self.get_claim(jwt_auth_settings.AUTHN_MULTI_FACTOR_EXPIRATION_CLAIM))

    @property
    def has_multi_factor_reference(self) -> bool:
        return self.has_claim(
            jwt_auth_settings.AUTHN_MULTI_FACTOR_REFERENCE_CLAIM)

    @property
    def multi_factor_reference(self) -> Any:
        return self.get_claim(jwt_auth_settings.AUTHN_MULTI_FACTOR_REFERENCE_CLAIM)

    @property
    def has_session_id(self) -> bool:
        return self.has_claim(
            jwt_auth_settings.AUTHN_SESSION_ID_CLAIM)

    @property
    def session_id(self) -> Any:
        return self.get_claim(jwt_auth_settings.AUTHN_SESSION_ID_CLAIM)

    @property
    def has_refresh_token_id(self) -> bool:
        return self.has_claim(jwt_auth_settings.AUTHN_REFRESH_TOKEN_ID_CLAIM)

    @property
    def refresh_token_id(self) -> Any:
        return self.get_claim(jwt_auth_settings.AUTHN_REFRESH_TOKEN_ID_CLAIM)

    @property
    def platform_type(self) -> Any:
        return self.get_claim(jwt_auth_settings.AUTHN_PLATFORM_TYPE_CLAIM)

    @property
    def is_mobile(self) -> bool:
        return self.platform_type == PLATFORM_TYPE_MOBILE

    @property
    def has_tenant_id(self) -> bool:
        return self.has_claim(jwt_auth_settings.TENANT_ID_CLAIM)

    @property
    def tenant_id(self) -> Any:
        return self.get_claim(jwt_auth_settings.TENANT_ID_CLAIM)

    @property
    def tenant_owner(self) -> Any:
        return self.get_claim(jwt_auth_settings.TENANT_OWNER_CLAIM)

    @property
    def role_ids(self) -> Any:
        return self.get_claim(jwt_auth_settings.RBAC_ROLE_IDS_CLAIM)

    def has_claim(self, claim: str) -> bool:
        return claim in self.payload

    def get_claim(self, claim: str) -> Any:
        try:
            return self.payload[claim]
        except KeyError:
            raise TokenError(claim)

    def set_jti(self) -> None:
        """
        Populates the configured jti claim of a token with a string where there
        is a negligible probability that the same string will be chosen at a
        later time.

        See here:
        https://tools.ietf.org/html/rfc7519#section-4.1.7
        """
        self._set_claim(jwt_settings.TOKEN_ID_CLAIM, uuid4().hex)

    def set_exp(
        self,
        from_time: Optional[datetime] = None,
        lifetime: Optional[timedelta] = None,
    ) -> None:
        """
        Updates the expiration time of a token.

        See here:
        https://tools.ietf.org/html/rfc7519#section-4.1.4
        """
        if from_time is None:
            from_time = self.current_time

        if lifetime is None:
            lifetime = self.lifetime
        self._set_claim(
            jwt_settings.EXPIRATION_CLAIM,
            datetime_to_epoch(from_time + lifetime))

    def set_mfe(
            self,
            from_time: Optional[datetime] = None,
            lifetime: Optional[timedelta] = None
    ):
        if from_time is None:
            from_time = self.current_time
        if lifetime is None:
            lifetime = jwt_auth_settings.AUTHN_MULTI_FACTOR_SESSION_LIFETIME
        self._set_claim(
            jwt_auth_settings.AUTHN_MULTI_FACTOR_EXPIRATION_CLAIM,
            datetime_to_epoch(from_time + lifetime))

    def set_iat(self, at_time: Optional[datetime] = None) -> None:
        """
        Updates the time at which the token was issued.

        See here:
        https://tools.ietf.org/html/rfc7519#section-4.1.6
        """
        if at_time is None:
            at_time = self.current_time
        self._set_claim(
            jwt_settings.ISSUED_AT_CLAIM,
            datetime_to_epoch(at_time))

    @property
    def token_backend(self) -> EvercoreJWTBackend:
        if self._token_backend is None:
            self._token_backend = import_string(
                "rest_framework_simplejwt.state.token_backend"
            )
        return self._token_backend

    def get_token_backend(self) -> EvercoreJWTBackend:
        # Backward compatibility.
        return self.token_backend


class AccessToken(Token):
    token_type = "access"
    lifetime = jwt_auth_settings.ACCESS_TOKEN_LIFETIME


class RefreshToken(Token):
    token_type = "refresh"
    lifetime = jwt_auth_settings.REFRESH_TOKEN_LIFETIME


# class RefreshToken(Token):
#     token_type = "refresh"
#     lifetime = api_settings.REFRESH_TOKEN_LIFETIME
#     no_copy_claims = (
#         api_settings.TOKEN_TYPE_CLAIM,
#         "exp",
#         # Both of these claims are included even though they may be the same.
#         # It seems possible that a third party token might have a custom or
#         # namespaced JTI claim as well as a default "jti" claim.  In that case,
#         # we wouldn't want to copy either one.
#         api_settings.JTI_CLAIM,
#         "jti",
#     )
#     access_token_class = AccessToken
#
#     @property
#     def access_token(self) -> AccessToken:
#         """
#         Returns an access token created from this refresh token.  Copies all
#         claims present in this refresh token to the new access token except
#         those claims listed in the `no_copy_claims` attribute.
#         """
#         access = self.access_token_class()
#
#         # Use instantiation time of refresh token as relative timestamp for
#         # access token "exp" claim.  This ensures that both a refresh and
#         # access token expire relative to the same time if they are created as
#         # a pair.
#         access.set_exp(from_time=self.current_time)
#
#         no_copy = self.no_copy_claims
#         for claim, value in self.payload.items():
#             if claim in no_copy:
#                 continue
#             access[claim] = value
#
#         return access
#
#
# class UntypedToken(Token):
#     token_type = "untyped"
#     lifetime = timedelta(seconds=0)
#
#     def verify_token_type(self) -> None:
#         """
#         Untyped tokens do not verify the "token_type" claim.  This is useful
#         when performing general validation of a token's signature and other
#         properties which do not relate to the token's intended use.
#         """
#         pass
