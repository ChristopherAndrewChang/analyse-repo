from __future__ import annotations
from typing import TYPE_CHECKING

import logging

import grpc

from idvalid_integration import _constants

from idvalid_integration.protos.cryptography.asymmetric.key_pb2 import (
    Algorithm,
    KeyPair,
    GenerateRequest,
    GenerateResponse,
    SignRequest,
    SignResponse,
    VerifyRequest,
    VerifyResponse,
)
from idvalid_integration.protos.cryptography.asymmetric.key_pb2_grpc import (
    KeyStub
)
from idvalid_integration.rpc.decorators import auto_channel

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    # messages
    "Algorithm",
    "KeyPair",
    "GenerateRequest",
    "GenerateResponse",
    "SignRequest",
    "SignResponse",
    "VerifyRequest",
    "VerifyResponse",

    # stubs
    "KeyStub",

    # functions
    "generate",
    "sign",
    "verify",
)


@auto_channel(setting_name=_constants.CRYPTOGRAPHY_GRPC_SETTING_NAME)
def generate(
        channel: grpc.Channel,
        message: GenerateRequest,
) -> GenerateResponse:
    stub = KeyStub(channel)
    try:
        logger.debug("send grpc request")
        return stub.Generate(message)
    except grpc.RpcError:
        raise


@auto_channel(setting_name=_constants.CRYPTOGRAPHY_GRPC_SETTING_NAME)
def sign(
        channel: grpc.Channel,
        message: SignRequest
) -> SignResponse:
    stub = KeyStub(channel)
    try:
        return stub.Sign(message)
    except grpc.RpcError:
        raise


@auto_channel(setting_name=_constants.CRYPTOGRAPHY_GRPC_SETTING_NAME)
def verify(
        channel: grpc.Channel,
        message: VerifyRequest
) -> VerifyResponse:
    stub = KeyStub(channel)
    try:
        return stub.Verify(message)
    except grpc.RpcError:
        raise
