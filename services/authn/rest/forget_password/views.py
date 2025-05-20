from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT

from idvalid_core.rest.permissions import DeviceCookieRequired

from authn.models import ForgetPassword
from authn.rest.permissions import OtpTokenPermission, PlatformPermission

from .serializers import CreateSerializer, ResetPasswordSerializer

if TYPE_CHECKING:
    from rest_framework.request import Request


logger = logging.getLogger(__name__)
__all__ = ("CreateView", "ResetPasswordView")


class CreateView(CreateAPIView):
    authentication_classes = ()
    permission_classes = (DeviceCookieRequired, PlatformPermission)
    serializer_class = CreateSerializer


class ResetPasswordView(GenericAPIView):
    authentication_classes = ()
    permission_classes = (DeviceCookieRequired, OtpTokenPermission, PlatformPermission)
    serializer_class = ResetPasswordSerializer
    queryset = ForgetPassword.objects.active().select_related(
        "user", "otp_token")
    lookup_field = "subid"

    def post(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=HTTP_204_NO_CONTENT)
