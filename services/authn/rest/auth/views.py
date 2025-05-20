from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT
from rest_framework.viewsets import GenericViewSet

from rest_framework_simplejwt.authentication import (
    AUTH_HEADER_TYPES,)
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.views import (
    TokenRefreshView as o_TokenRefreshView,)

from evercore_jwt_auth.rest_framework.authentication import (
    JWTRefreshAuthentication,
    JWTAuthentication,
)

from idvalid_core.rest.permissions import DeviceCookieRequired

from authn.models import PasskeyChallenge

from ..permissions import PlatformPermission

from .serializers import (
    PasskeyLoginSerializer,
    LoginSerializer,
    EmailLoginSerializer,
    PhoneLoginSerializer,
)

if TYPE_CHECKING:
    from rest_framework.request import Request
    from authn.tokens import AccessToken


logger = logging.getLogger(__name__)
__all__ = (
    "LoginView",
    "EmailLoginView",
    "PhoneLoginView",
    "PasskeyLoginView",

    "TokenRefreshView",

    "LogoutView",
)


class BaseLoginView(CreateAPIView):
    authentication_classes = ()
    permission_classes = (
        DeviceCookieRequired,
        PlatformPermission,
    )
    www_authenticate_realm = "api"

    def get_authenticate_header(self, request: Request) -> str:
        return '{} realm="{}"'.format(
            AUTH_HEADER_TYPES[0],
            self.www_authenticate_realm,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=HTTP_200_OK)


class LoginView(BaseLoginView):
    serializer_class = LoginSerializer


class EmailLoginView(BaseLoginView):
    serializer_class = EmailLoginSerializer


class PhoneLoginView(BaseLoginView):
    serializer_class = PhoneLoginSerializer


class PasskeyLoginView(GenericViewSet):
    authentication_classes = ()
    permission_classes = (
        DeviceCookieRequired,
        PlatformPermission,
    )
    serializer_class = PasskeyLoginSerializer
    www_authenticate_realm = "api"
    lookup_field = "subid"

    def get_authenticate_header(self, request: Request) -> str:
        return '{} realm="{}"'.format(
            AUTH_HEADER_TYPES[0],
            self.www_authenticate_realm,
        )

    def get_queryset(self):
        return PasskeyChallenge.objects.for_authentication()

    def challenge(self, request: Request, *args, **kwargs) -> Response:
        instance = PasskeyChallenge.objects.create_authentication()
        return Response({
            "id": instance.subid,
            "publicKey": instance.get_options()
        })

    def verify(self, request: Request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


class TokenRefreshView(o_TokenRefreshView):
    authentication_classes = (JWTRefreshAuthentication,)
    permission_classes = (
        IsAuthenticated,
        DeviceCookieRequired,
        PlatformPermission,
    )


class LogoutView(CreateAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (
        IsAuthenticated,
        DeviceCookieRequired,
        PlatformPermission,
    )

    def create(self, request, *args, **kwargs):
        token = request.auth  # type: AccessToken
        session = token.get_session_instance()
        if session:
            session.delete()
        return Response(status=HTTP_204_NO_CONTENT)
