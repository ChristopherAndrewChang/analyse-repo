from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_framework_simplejwt.authentication import JWTAuthentication

if TYPE_CHECKING:
    from rest_framework.request import Request
    from authn.models import User


logger = logging.getLogger(__name__)
__all__ = (
    "SummaryView",
)


class SummaryView(GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (
        # PlatformPermission,
        IsAuthenticated,
    )

    def get(self, request: Request, *args, **kwargs):
        user = request.user  # type: User
        return Response({
            "authenticator": user.has_totp(),
            "security_code": user.has_security_code(),
        })
