from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from rest_framework import status
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from evercore_jwt_auth.rest_framework.authentication import JWTAuthentication

from idvalid_core.rest.permissions import DeviceCookieRequired

from authn_sdk.rest.permissions import MobileAccessPermission

from authn.rest.permissions import (
    PlatformPermission,
)

from .serializers import (
    ListSerializer,
    VerifySerializer,
)

if TYPE_CHECKING:
    from rest_framework.request import Request
    from authn.models import User, MobileOTP


logger = logging.getLogger(__name__)
__all__ = (
    "MobileOtpViewSet",
)


class MobileOtpViewSet(GenericViewSet):
    authentication_classes = (JWTAuthentication,)
    # print((~MobileAccessPermission).__dict__)
    permission_classes = (
        DeviceCookieRequired,
        PlatformPermission,
        IsAuthenticated,
        MobileAccessPermission,
    )
    lookup_field = "subid"

    def get_queryset(self):
        user = self.request.user  # type: User
        return user.mobileotp_set.alive()

    def get_serializer_class(self):
        action = self.action
        if action == "list":
            return ListSerializer
        elif action == "verify":
            return VerifySerializer
        return super().get_serializer_class()

    def list(self, request: Request, *args, **kwargs) -> Response:
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def verify(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def reject(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()  # type: MobileOTP
        instance.reject()
        return Response(status=status.HTTP_204_NO_CONTENT)
