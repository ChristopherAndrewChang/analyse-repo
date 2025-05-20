from __future__ import annotations
from typing import TYPE_CHECKING

import logging

import grpc

from idvalid_integration import _constants
from idvalid_integration.protos.authn.user_pb2 import (
    CreateRequest,
    CreateResponse,
)
from idvalid_integration.protos.models.authn_pb2 import (
    CreateUser,
)
from idvalid_integration.protos.authn.user_pb2_grpc import (
    UserStub
)
from idvalid_integration.rpc.decorators import auto_channel

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    # messages
    "CreateRequest",
    "CreateResponse",
    "CreateUser",

    # stubs
    "UserStub",

    # functions
    "create",
)


@auto_channel(setting_name=_constants.AUTHN_GRPC_SETTINGS_NAME)
def create(
        channel: grpc.Channel, *,
        message: CreateRequest
) -> CreateResponse:
    stub = UserStub(channel)
    try:
        return stub.Create(message)
    except grpc.RpcError:
        raise
