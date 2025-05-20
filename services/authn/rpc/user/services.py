from __future__ import annotations
from typing import TYPE_CHECKING

import logging
import grpc

from evercore_grpc.framework.generics import GenericService

from idvalid_integration.protos.authn import user_pb2_grpc

# from authn.models import User

from .serializers import CreateSerializer

if TYPE_CHECKING:
    from idvalid_integration.rpc.authn.user import (
        CreateRequest,
        CreateResponse,
    )


logger = logging.getLogger(__name__)
__all__ = ("UserService",)


class UserService(GenericService, user_pb2_grpc.UserServicer):
    serializer_class = CreateSerializer

    def Create(
            self, request: CreateRequest,
            context: grpc.ServicerContext
    ) -> CreateResponse:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.message
