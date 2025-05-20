from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from .serializers import OTPSerializer, CreateSerializer

if TYPE_CHECKING:
    from enrollment.models import Otp


logger = logging.getLogger(__name__)
__all__ = ("EnrollmentView", "CreateView",)


class EnrollmentView(CreateAPIView):
    serializer_class = OTPSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response = Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        instance = serializer.instance  # type: Otp
        response.set_cookie(
            "otp_id", instance.otp_id,
            expires=instance.expires,
            domain=".idval.id",
            secure=True,
            httponly=True,
            samesite="lax"
        )
        return response


class CreateView(CreateAPIView):
    serializer_class = CreateSerializer
    authentication_classes = ()
