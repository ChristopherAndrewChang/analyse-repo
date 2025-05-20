from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from google.protobuf.duration_pb2 import Duration

from enrollment.settings import enrollment_settings

from idvalid_integration.rpc.otp.code import (
    create,
    CreateRequest
)
from idvalid_integration.rpc.cryptography.asymmetric.key import (
    verify,
    VerifyRequest
)

if TYPE_CHECKING:
    from idvalid_integration.rpc.otp.code import (
        CreateResponse, ConfirmResponse)
    # from idvalid_integration.rpc.cryptography.asymmetric.key import (
    #     VerifyResponse,)
    from enrollment.models import Enrollment, Otp


logger = logging.getLogger(__name__)
__alL__ = (
    "generate_otp",
    "verify_otp_signature",
)


def generate_otp(instance: Enrollment, **kwargs) -> CreateResponse:
    if not instance.subid:
        raise ValueError("instance subid must be set")
    duration = Duration()
    duration.FromSeconds(enrollment_settings.OTP_DURATION)
    data = {
        "email": CreateRequest.EmailOtp(value=instance.email),
        "expires_in": duration,
        "usage": "email-enrollment",
        "issuer": "enrollment",
        "ref_id": instance.subid,
        **kwargs
    }
    if last_otp_id := instance.last_otp_id:
        data["suppress"] = last_otp_id
    return create(message=CreateRequest(**data))


def verify_otp_signature(instance: Otp, signature: bytes, **kwargs) -> bool:
    data = {
        "public_key": instance.key,
        "signature": signature,
        "data": instance.otp_id.encode('utf-8')
    }
    return verify(message=VerifyRequest(**data)).valid
