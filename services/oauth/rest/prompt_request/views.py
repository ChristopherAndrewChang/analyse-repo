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

from oauth.models import PromptRequest

if TYPE_CHECKING:
    from oauth.models import IDToken


__all__ = (
    "GenerateView",
    "RetrieveView",
)


class GenerateView(GenericAPIView):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (
        IsAuthenticated,
    )

    def post(self, request, *args, **kwargs) -> Response:
        token = request.auth  # type: IDToken
        expires = timezone.now() + timedelta(seconds=60 * 5)
        instance = PromptRequest.objects.create(
            application_id=token.application_id,
            user_id=token.user_id,
            expires=expires)  # type: PromptRequest
        if fbt := request.headers.get("x-idv-fbt"):
            application = token.application
            body = f"Application {application.name.title()} requests an OTP"
            messaging.send(messaging.Message(
                notification=messaging.Notification(
                    title="Prompt Request", body=body
                ),
                token=fbt,
                data={
                    "idv_request_id": instance.subid,
                    "idv_notification_type": "prompt-request"
                },
            ))
        return Response({
            "id": instance.subid,
            "expires": instance.expires,
        }, status=status.HTTP_201_CREATED)


class RetrieveView(GenerateView):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (
        IsAuthenticated,
    )
    lookup_field = "subid"

    def get_queryset(self):
        token = self.request.auth  # type: IDToken
        return PromptRequest.objects.filter(
            application_id=token.application_id,
            user_id=token.user_id)

    def get(self, request, *args, **kwargs):
        instance = self.get_object()  # type: PromptRequest
        return Response({
            "answer": instance.answer,
            "answer_time": instance.answer_time
        })
