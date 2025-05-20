from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_framework_simplejwt.authentication import JWTAuthentication

from idvalid_core.rest.permissions import DeviceCookieRequired

from authn.rest.permissions import (
    PlatformPermission,
    LoginTwoFARequired,
    TwoFARequired,
)

from ..permissions import HasSecurityCode
from ..serializers import (
    SetSecurityCodeSerializer,
    ChangeSecurityCodeSerializer,
    VerifySecurityCodeSerializer,
)

if TYPE_CHECKING:
    from rest_framework.request import Request
    from authn.models import User


logger = logging.getLogger(__name__)
__all__ = (
    "SecurityCodeView",
)


class SecurityCodeView(GenericAPIView):
    request: "Request"
    authentication_classes = (JWTAuthentication,)

    def get_permissions(self):
        method = self.request.method
        if method == "PUT":
            # update pin
            self.permission_classes = (
                DeviceCookieRequired,
                PlatformPermission,
                IsAuthenticated,
                LoginTwoFARequired,
                TwoFARequired,
            )
        elif method == "POST":
            # verify
            self.permission_classes = (
                DeviceCookieRequired,
                PlatformPermission,
                IsAuthenticated,
                HasSecurityCode,
            )
        elif method == "DELETE":
            # disabled
            self.permission_classes = (
                DeviceCookieRequired,
                PlatformPermission,
                IsAuthenticated,
                LoginTwoFARequired,
                TwoFARequired,
                HasSecurityCode,
            )
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return VerifySecurityCodeSerializer
        return super().get_serializer_class()

    def put(self, request: Request, *args, **kwargs) -> Response:
        user = request.user  # type: User
        serializer_class = (
            ChangeSecurityCodeSerializer
            if user.has_security_code() else
            SetSecurityCodeSerializer
        )
        serializer = serializer_class(
            data=request.data,
            context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)

    def delete(self, request: Request, *args, **kwargs) -> Response:
        instance = request.user  # type: User
        instance.remove_security_code()
        return Response(status=status.HTTP_204_NO_CONTENT)
