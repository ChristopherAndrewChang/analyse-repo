from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from rest_framework import status
from rest_framework.exceptions import Throttled
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from evercore_jwt_auth.rest_framework.authentication import JWTAuthentication

from idvalid_core.rest.permissions import DeviceCookieRequired

from authn_sdk.rest.permissions import NonMobileAccessPermission
from authn.models import (
    CooldownError,
)
from authn.rest.permissions import (
    PlatformPermission,
    HasAuthenticator,
    HasSecurityCode,
    HasBackupCode,
    HasEmail,
    HasPasskey,
    HasMobileLoggedIn,
)

from .serializers import (
    AuthenticatorSerializer,
    SecurityCodeSerializer,
    BackupCodeSerializer,
    EmailSerializer,
    PasskeySerializer,
    CreateMobileSerializer,
    MobileSerializer,
)

if TYPE_CHECKING:
    from rest_framework.request import Request
    from authn.models import (
        User,
        EmailOTP,
    )


logger = logging.getLogger(__name__)
__all__ = (
    "BaseMultiFactorViewSet",
    "SummaryViewSet",
    "AuthenticatorViewSet",
    "SecurityCodeViewSet",
    "BackupCodeViewSet",
    "EmailViewSet",
    "MobileViewSet",
    "PasskeyViewSet",
)


class BaseMultiFactorViewSet(GenericViewSet):
    request: "Request"
    authentication_classes = (JWTAuthentication,)

    def get_instance(self):
        return self.request.user

    def challenge(self, request: Request, *args, **kwargs) -> Response:
        raise NotImplementedError

    def verify(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(self.get_instance(), data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data or None
        return Response(
            data,
            status=(
                status.HTTP_200_OK
                if data else
                status.HTTP_204_NO_CONTENT
            )
        )


class SummaryViewSet(GenericViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (
        DeviceCookieRequired,
        PlatformPermission,
        IsAuthenticated,
    )

    def list(self, request: Request, *args, **kwargs):
        user = request.user  # type: User
        return Response(user.get_mf_summary(request))


class EmailViewSet(BaseMultiFactorViewSet):
    permission_classes = (
        DeviceCookieRequired,
        PlatformPermission,
        IsAuthenticated,
        HasEmail,
    )
    serializer_class = EmailSerializer

    def challenge(self, request: Request, *args, **kwargs) -> Response:
        user = request.user  # type: User
        instance, _ = user.emailotp_set.get_or_create()  # type: EmailOTP
        if not instance:
            raise Exception("user has no email otp")
        try:
            instance.generate_challenge()
        except CooldownError:
            raise Throttled()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MobileViewSet(BaseMultiFactorViewSet):
    permission_classes = (
        DeviceCookieRequired,
        PlatformPermission,
        IsAuthenticated,
        NonMobileAccessPermission,
        HasMobileLoggedIn,
    )
    lookup_field = "subid"

    def get_queryset(self):
        return self.request.user.mobileotp_set.confirmed()

    def get_instance(self):
        return self.get_object()

    def get_serializer_class(self):
        action = self.action
        if action == "challenge":
            return CreateMobileSerializer
        if action == "verify":
            return MobileSerializer
        return super().get_serializer_class()

    def challenge(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AuthenticatorViewSet(BaseMultiFactorViewSet):
    permission_classes = (
        DeviceCookieRequired,
        PlatformPermission,
        IsAuthenticated,
        HasAuthenticator,
    )
    serializer_class = AuthenticatorSerializer


class SecurityCodeViewSet(BaseMultiFactorViewSet):
    permission_classes = (
        DeviceCookieRequired,
        PlatformPermission,
        IsAuthenticated,
        HasSecurityCode,
    )
    serializer_class = SecurityCodeSerializer


class BackupCodeViewSet(BaseMultiFactorViewSet):
    permission_classes = (
        DeviceCookieRequired,
        PlatformPermission,
        IsAuthenticated,
        HasBackupCode,
    )
    serializer_class = BackupCodeSerializer


class PasskeyViewSet(BaseMultiFactorViewSet):
    permission_classes = (
        DeviceCookieRequired,
        PlatformPermission,
        IsAuthenticated,
        HasPasskey,
    )
    serializer_class = PasskeySerializer
    lookup_field = "subid"

    def get_queryset(self):
        return self.request.user.passkey_challenges.for_authentication()

    def get_instance(self):
        return self.get_object()

    def challenge(self, request: Request, *args, **kwargs) -> Response:
        user = request.user  # type: User
        challenge = user.passkey_challenges.create_authentication()
        return Response({
            "id": challenge.subid,
            "publicKey": challenge.get_options()
        })
