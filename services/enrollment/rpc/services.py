from __future__ import annotations
from typing import TYPE_CHECKING

import logging
import grpc

from evercore_grpc.framework.generics import GenericService

from idvalid_integration.rpc.enrollment.email import (
    GetEmailResponse,
)
from idvalid_integration.protos.enrollment import enrollment_pb2_grpc

from enrollment.models import Otp

from .serializers import ConfirmSerializer, GetEmailSerializer

if TYPE_CHECKING:
    from idvalid_integration.rpc.enrollment.email import (
        ConfirmRequest,
        ConfirmResponse,
        GetEmailRequest,
    )


logger = logging.getLogger(__name__)
__all__ = ("EnrollmentServicer",)


class EnrollmentServicer(GenericService, enrollment_pb2_grpc.EnrollmentServicer):
    serializer_class = ConfirmSerializer
    lookup_field = "subid"
    lookup_request_field = "id"
    queryset = Otp.objects.filter(
        is_confirmed=False
    ).select_related("enrollment")

    def get_serializer_class(self):
        if self.action == "GetEmail":
            return GetEmailSerializer
        return super().get_serializer_class()

    def GetEmail(
            self, request: GetEmailRequest, context: grpc.ServicerContext
    ) -> GetEmailResponse:
        instance = self.get_object()  # type: Otp
        serializer = self.get_serializer(instance, data=request)
        serializer.is_valid(raise_exception=True)

        return GetEmailResponse(email=instance.enrollment.email)

    def Confirm(
            self, request: ConfirmRequest, context: grpc.ServicerContext
    ) -> ConfirmResponse:
        instance = self.get_object()  # type: Otp
        serializer = self.get_serializer(instance, data=request)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return serializer.message
