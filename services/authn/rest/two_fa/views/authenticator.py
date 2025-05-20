from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_framework_simplejwt.authentication import JWTAuthentication

from idvalid_core.rest.permissions import DeviceCookieRequired

from authn.models import TOTP

from authn.rest.permissions import (
    PlatformPermission,
    LoginTwoFARequired,
    TwoFARequired,
)

from ..permissions import HasAuthenticator
from ..serializers import (
    ConfirmAuthenticatorSerializer,
    VerifyAuthenticatorSerializer
)

if TYPE_CHECKING:
    from typing import Sequence
    from rest_framework.permissions import BasePermission
    from rest_framework.request import Request
    from authn.models import User


logger = logging.getLogger(__name__)
__all__ = (
    "AuthenticatorView",
    "ConfirmTOTPView",
)


class AuthenticatorView(GenericAPIView):
    request: "Request"
    authentication_classes = (JWTAuthentication,)

    def get_permissions(self) -> Sequence[BasePermission]:
        method = self.request.method
        if method == "GET":
            # generate
            self.permission_classes = (
                DeviceCookieRequired,
                PlatformPermission,
                IsAuthenticated,
                LoginTwoFARequired,
                TwoFARequired
            )
        elif method == "POST":
            # verify
            self.permission_classes = (
                DeviceCookieRequired,
                PlatformPermission,
                IsAuthenticated,
                HasAuthenticator,
            )
        elif method == "DELETE":
            # disabled
            self.permission_classes = (
                DeviceCookieRequired,
                PlatformPermission,
                IsAuthenticated,
                LoginTwoFARequired,
                TwoFARequired,
                HasAuthenticator,
            )
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return VerifyAuthenticatorSerializer
        return super().get_serializer_class()

    def get(self, request: Request, *args, **kwargs) -> Response:
        user = request.user  # type: User
        instance = TOTP.objects.create(
            description="user",
            created_by=user
        )  # type: TOTP
        return Response({
            "pk": instance.subid,
            "url": instance.config_url(user.username)
        })

    def post(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)

    def delete(self, request: Request, *args, **kwargs) -> Response:
        instance = request.user  # type: User
        instance.remove_totp()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ConfirmTOTPView(GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (
        DeviceCookieRequired,
        PlatformPermission,
        IsAuthenticated,
        LoginTwoFARequired,
    )
    queryset = TOTP.objects.filter(
        confirmed=False,
        disabled=False
    )
    lookup_field = "subid"

    def get_queryset(self):
        return super().get_queryset().filter(
            created_by=self.request.user)

    def put(self, request: Request, *args, **kwargs):
        instance = self.get_object()
        serializer = ConfirmAuthenticatorSerializer(
            instance,
            data=request.data,
            context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
