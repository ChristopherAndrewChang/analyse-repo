from __future__ import annotations
from typing import TYPE_CHECKING

import logging
import grpc

from evercore_grpc.framework.generics import GenericService

from idvalid_integration.rpc.otp.code import (
    CreateRequest,
    CreateResponse,
    ConfirmRequest,
    ConfirmResponse,
)
from idvalid_integration.protos.otp import code_pb2_grpc

from otp.models import Code

from .serializers import CodeSerializer

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "CodeService",
)


class CodeService(GenericService, code_pb2_grpc.CodeServicer):
    serializer_class = CodeSerializer
    lookup_field = "subid"
    lookup_request_field = "id"
    queryset = Code.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "Confirm":
            return queryset.confirmation()
        return queryset

    def Create(self, request: CreateRequest,
               context: grpc.ServicerContext) -> CreateResponse:
        serializer = self.get_serializer(data=request)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.message

    def Confirm(self, request: ConfirmRequest,
                context: grpc.ServicerContext) -> ConfirmResponse:
        instance = self.get_object()  # type: Code
        instance.confirm()
        return ConfirmResponse(success=True)
