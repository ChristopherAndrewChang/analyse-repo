from __future__ import annotations
from typing import TYPE_CHECKING

from django.db.models.expressions import F
from django.utils import timezone

# from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from evercore_jwt_auth.rest_framework.authentication import JWTStatelessUserAuthentication
from evercore_jwt_auth.rest_framework.permissions import MultiFactorSessionAlive

from oauth.models import OtpRequest

if TYPE_CHECKING:
    from rest_framework.request import Request


__all__ = (
    "ListView",
    "DetailView",
)


class ListView(GenericAPIView):
    authentication_classes = (JWTStatelessUserAuthentication,)
    permission_classes = (
        IsAuthenticated,
        MultiFactorSessionAlive,
    )

    def get_queryset(self):
        return OtpRequest.objects.filter(
            user_id=self.request.user.pk,
            expires__gt=timezone.now()
        ).select_related(
            "application"
        ).values(
            "otp",
            "expires",
            application_name=F("application__name"),
        )

    def get(self, request: Request, *args, **kwargs):
        return Response(self.filter_queryset(self.get_queryset()))


class DetailView(ListView):
    lookup_field = "subid"

    def get(self, request: Request, *args, **kwargs) -> Response:
        return Response(self.get_object())
