from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from webauthn.helpers.exceptions import WebAuthnException

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from evercore_jwt_auth.rest_framework.authentication import JWTAuthentication
from evercore_jwt_auth.rest_framework.permissions import (
    MultiFactorSessionAlive,
)

from idvalid_core.rest.permissions import DeviceCookieRequired

from authn.rest.permissions import HasPasskey

if TYPE_CHECKING:
    from rest_framework.request import Request
    from authn.models import User, PasskeyChallenge


logger = logging.getLogger(__name__)
__all__ = (
    "RegistrationViewSet",
    "PasskeyViewSet",
)


class RegistrationViewSet(GenericViewSet):
    request: "Request"
    authentication_classes = (JWTAuthentication,)
    permission_classes = (
        DeviceCookieRequired,
        IsAuthenticated,
        MultiFactorSessionAlive,
    )
    lookup_field = "subid"

    def get_queryset(self):
        return self.request.user.passkey_challenges.for_registration()

    def challenge(self, request: Request, *args, **kwargs) -> Response:
        user = request.user  # type: User
        challenge = user.passkey_challenges.create_registration()
        return Response({
            "id": challenge.subid,
            "publicKey": challenge.get_options()
        })

    def verify(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()  # type: PasskeyChallenge
        try:
            instance.verify(request.data)
        except WebAuthnException as e:
            raise ValidationError(str(e))
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasskeyViewSet(GenericViewSet):
    request: "Request"
    authentication_classes = (JWTAuthentication,)
    lookup_field = "subid"

    def get_queryset(self):
        return self.request.user.passkeys.active()

    def get_permissions(self):
        action = self.action
        base_perms = (
            DeviceCookieRequired,
            IsAuthenticated,
            MultiFactorSessionAlive,
        )
        if action == "destroy":
            self.permission_classes = base_perms + (
                HasPasskey,)
        else:
            self.permission_classes = base_perms
        return super().get_permissions()

    def list(self, request: Request, *args, **kwargs) -> Response:
        return Response(
            self.filter_queryset(
                self.get_queryset()
            ).order_by(
                "created_at").values(
                "subid",
                "created_at",
                "last_used_at",
            )
        )

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
