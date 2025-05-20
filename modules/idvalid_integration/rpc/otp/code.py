from __future__ import annotations
from typing import TYPE_CHECKING

import logging

import grpc

from idvalid_integration import _constants
from idvalid_integration.protos.otp.code_pb2 import (
    CreateRequest,
    CreateResponse,
    ConfirmRequest,
    ConfirmResponse,
)
from idvalid_integration.protos.otp.code_pb2_grpc import (
    CodeStub
)
from idvalid_integration.rpc.decorators import auto_channel

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    # messages
    "CreateRequest",
    "CreateResponse",
    "ConfirmRequest",
    "ConfirmResponse",

    # stubs
    "CodeStub",

    # functions
    "create",
    "confirm",
)


@auto_channel(setting_name=_constants.OTP_GRPC_SETTING_NAME)
def create(
        channel: grpc.Channel, *,
        message: CreateRequest,
) -> CreateResponse:
    stub = CodeStub(channel)
    try:
        return stub.Create(message)
    except grpc.RpcError:
        raise


@auto_channel(setting_name=_constants.OTP_GRPC_SETTING_NAME)
def confirm(
        channel: grpc.Channel, *,
        message: ConfirmRequest
) -> ConfirmResponse:
    stub = CodeStub(channel)
    try:
        return stub.Confirm(message)
    except grpc.RpcError:
        raise
