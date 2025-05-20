from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from idvalid_integration.rpc.cryptography.asymmetric.key import (
    Algorithm,

    generate,
    GenerateRequest,
    GenerateResponse,

    sign,
    SignRequest,
    SignResponse,
)

if TYPE_CHECKING:
    from otp.models import Code


logger = logging.getLogger(__name__)
__all__ = ("generate_key_pair", "sign_code",)


def generate_key_pair() -> GenerateResponse:
    return generate(
        message=GenerateRequest(
            algorithm=Algorithm.ALGORITHM_ED25519
        )
    )


def sign_code(code: Code) -> SignResponse:
    return sign(
        message=SignRequest(
            private_key=code.key,
            data=code.subid.encode("utf-8")
        )
    )
