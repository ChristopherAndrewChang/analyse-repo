from __future__ import annotations
from typing import TYPE_CHECKING

import logging

import grpc

from idvalid_integration import _constants
from idvalid_integration.protos.enrollment.enrollment_pb2 import (
    GetEmailRequest,
    GetEmailResponse,
    ConfirmRequest,
    ConfirmResponse
)
from idvalid_integration.protos.enrollment.enrollment_pb2_grpc import (
    EnrollmentStub
)
from idvalid_integration.rpc.decorators import auto_channel

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    # messages
    "GetEmailRequest",
    "GetEmailResponse",
    "ConfirmRequest",
    "ConfirmResponse",

    # stubs
    "EnrollmentStub",

    # functions
    "confirm",
    "get_email",
)


@auto_channel(setting_name=_constants.ENROLLMENT_GRPC_SETTING_NAME)
def get_email(
        channel: grpc.Channel, *,
        message: GetEmailRequest
) -> GetEmailResponse:
    stub = EnrollmentStub(channel)
    try:
        return stub.GetEmail(message)
    except grpc.RpcError:
        raise


@auto_channel(setting_name=_constants.ENROLLMENT_GRPC_SETTING_NAME)
def confirm(
        channel: grpc.Channel, *,
        message: ConfirmRequest,
) -> ConfirmResponse:
    stub = EnrollmentStub(channel)
    try:
        return stub.Confirm(message)
    except grpc.RpcError:
        raise
