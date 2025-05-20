from __future__ import annotations
from typing import TYPE_CHECKING

from datetime import timedelta

from firebase_admin import messaging

from django.utils import timezone

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from oauth2_provider.contrib.rest_framework.authentication import (
    OAuth2Authentication,
)

from oauth.models import OtpRequest

from .serializers import VerifySerializer

if TYPE_CHECKING:
    from oauth.models import IDToken


_all__ = (
    "GenerateView",
    "VerifyView",
)


class GenerateView(GenericAPIView):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (
        IsAuthenticated,
    )

    def post(self, request, *args, **kwargs) -> Response:
        token = request.auth  # type: IDToken
        import random, string
        otp = "".join(random.choices(string.digits, k=6))
        expires = timezone.now() + timedelta(seconds=60 * 5)
        instance, created = OtpRequest.objects.get_or_create(
            application_id=token.application_id,
            user_id=token.user_id,
            defaults={
                "otp": otp,
                "expires": expires
            }
        )  # type: OtpRequest, bool
        if not created:
            instance.otp = otp
            instance.expires = expires
            instance.save(update_fields=["otp", "expires"])
        if fbt := request.headers.get("x-idv-fbt"):
            application = token.application
            body = f"Application {application.name.title()} requests an OTP"
            messaging.send(messaging.Message(
                notification=messaging.Notification(
                    title="OTP Request", body=body
                ),
                token=fbt,
                data={
                    "idv_request_id": instance.subid,
                    "idv_notification_type": "otp-request"
                },
            ))
        # serializer = self.get_serializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # self.perform_create(serializer)
        # headers = self.get_success_headers(serializer.data)
        return Response({
            "id": instance.subid,
            "expires": instance.expires,
        }, status=status.HTTP_201_CREATED)


class VerifyView(GenericAPIView):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (
        IsAuthenticated,
    )
    serializer_class = VerifySerializer
    lookup_field = "subid"

    def get_queryset(self):
        token = self.request.auth  # type: IDToken
        return OtpRequest.objects.filter(
            application_id=token.application_id,
            user_id=token.user_id)

    def post(self, request, *args, **kwargs):
        instance = self.get_object()  # type: OtpRequest
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        instance.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
