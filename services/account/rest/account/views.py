from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT

from idvalid_core.rest.permissions import DeviceCookieRequired

from account.models import Enrollment

from .permissions import CreateAccountPermission
from .serializers import CreateSerializer

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = ("CreateView",)


class CreateView(CreateAPIView):
    authentication_classes = ()
    permission_classes = (DeviceCookieRequired, CreateAccountPermission)
    serializer_class = CreateSerializer
    queryset = Enrollment.objects.active().select_related(
        "otp_token", "email")
    lookup_field = "subid"

    def get_serializer_context(self):
        result = super().get_serializer_context()
        result['enrollment'] = self.get_object()
        return result

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(status=HTTP_204_NO_CONTENT)
