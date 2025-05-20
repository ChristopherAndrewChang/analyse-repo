from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# from rest_framework_simplejwt.authentication import JWTAuthentication

from evercore_jwt_auth.rest_framework.authentication import JWTAuthentication
from evercore_jwt_auth.rest_framework.permissions import (
    MultiFactorAuthRequired,
    MultiFactorSessionAlive,
)

from idvalid_core.rest.permissions import DeviceCookieRequired

from authn.models import Enrollment, ChangeEmail
from authn.rest.permissions import (
    OtpTokenPermission,
    PlatformPermission,
)

from .serializers import (
    CreateSerializer,
    ChangePasswordSerializer,
    ProfileSerializer,
    CreateChangeEmailSerializer,
    VerifyChangeEmailSerializer,
)

if TYPE_CHECKING:
    from rest_framework.request import Request
    from authn.models import User


logger = logging.getLogger(__name__)
__all__ = (
    "CreateView",
    "ChangePasswordView",
    "ChangeEmailView",
    "LoginMethodView",
    "ProfileView",
)


class CreateView(CreateAPIView):
    authentication_classes = ()
    permission_classes = (
        DeviceCookieRequired,
        OtpTokenPermission,
        PlatformPermission,
    )
    serializer_class = CreateSerializer
    queryset = Enrollment.objects.active().select_related(
        "otp_token")
    lookup_field = "subid"

    def get_serializer_context(self):
        result = super().get_serializer_context()
        result['enrollment'] = self.get_object()
        return result

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangePasswordView(GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (
        DeviceCookieRequired,
        PlatformPermission,
        IsAuthenticated,
        MultiFactorSessionAlive,
    )
    serializer_class = ChangePasswordSerializer

    def post(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(
            instance=request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangeEmailView(GenericViewSet):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (
        DeviceCookieRequired,
        PlatformPermission,
        IsAuthenticated,
        MultiFactorSessionAlive,
        OtpTokenPermission,
    )
    serializer_class = CreateChangeEmailSerializer
    queryset = ChangeEmail.objects.active().select_related(
        "user", "otp_token")
    lookup_field = "subid"

    def get_serializer_class(self):
        if self.action == "create":
            return CreateChangeEmailSerializer
        elif self.action == "verify":
            return VerifyChangeEmailSerializer
        return super().get_serializer_class()

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data, status=status.HTTP_201_CREATED)

    def verify(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LoginMethodView(GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (
        DeviceCookieRequired,
        IsAuthenticated,
        MultiFactorAuthRequired,
    )

    def get(self, request: Request, *args, **kwargs) -> Response:
        user = request.user  # type: User
        phone = user.phone
        return Response({
            "email": user.email,
            "phone": phone.as_e164 if phone else phone
        })


class ProfileView(GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (
        DeviceCookieRequired,
        IsAuthenticated,
        MultiFactorAuthRequired,
    )
    serializer_class = ProfileSerializer

    def get(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(instance=request.user.profile)
        return Response(serializer.data)

    def put(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(
            instance=request.user.profile, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
