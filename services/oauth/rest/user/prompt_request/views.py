from __future__ import annotations
from typing import TYPE_CHECKING

from django.db.models.expressions import F
from django.utils import timezone

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from evercore_jwt_auth.rest_framework.authentication import (
    JWTStatelessUserAuthentication,
)
from evercore_jwt_auth.rest_framework.permissions import (
    MultiFactorSessionAlive,
)

from oauth.models import PromptRequest

from .serializers import AnswerSerializer

if TYPE_CHECKING:
    from rest_framework.request import Request
    from oauth.models import PromptQuerySet


__all__ = (
    "ListView",
    "DetailView",
)


class BaseQS:
    request: Request

    def get_queryset(self) -> PromptQuerySet:
        return PromptRequest.objects.filter(
            user_id=self.request.user.pk,
            expires__gt=timezone.now(),
            answer__isnull=True
        ).select_related(
            "application"
        )


class ListView(BaseQS, GenericAPIView):
    authentication_classes = (JWTStatelessUserAuthentication,)
    permission_classes = (
        IsAuthenticated,
        MultiFactorSessionAlive,
    )

    def get_queryset(self):
        return super().get_queryset().values(
            "expires",
            "subid",
            application_name=F("application__name")
        )

    def get(self, request: Request, *args, **kwargs) -> Response:
        return Response(self.filter_queryset(
            self.get_queryset()
        ))


class DetailView(BaseQS, GenericAPIView):
    authentication_classes = (JWTStatelessUserAuthentication,)
    permission_classes = (
        IsAuthenticated,
        MultiFactorSessionAlive,
    )
    serializer_class = AnswerSerializer
    lookup_field = "subid"

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.method == "GET":
            return qs.values(
                "expires",
                "subid",
                application_name=F("application__name")
            )
        return qs

    def get(self, request: Request, *args, **kwargs) -> Response:
        return Response(self.get_object())

    def post(self, request: Request, *args, **kwargs) -> Response:
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
