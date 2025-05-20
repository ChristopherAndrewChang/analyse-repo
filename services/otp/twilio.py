from __future__ import annotations
from typing import TYPE_CHECKING

from twilio.rest import Client

from otp.settings import otp_settings

if TYPE_CHECKING:
    from typing import Optional
    from twilio.rest.verify.v2.service import (
        ServiceContext as VerifyV2ServiceContext,
    )
    from twilio.rest.verify.v2.service.verification import (
        VerificationInstance,
    )


def get_default_client() -> Client:
    return Client(
        username=otp_settings.TWILIO_API_KEY,
        password=otp_settings.TWILIO_API_SECRET,
        account_sid=otp_settings.TWILIO_ACCOUNT_SID)


def get_default_verify_service(client: Client) -> VerifyV2ServiceContext:
    return client.verify.v2.services(otp_settings.TWILIO_VERIFY_SID)


class Twilio:
    def __init__(self, client: Client = None):
        self.client = client or get_default_client()
        self._verify_service: "Optional[VerifyV2ServiceContext]" = None

    @property
    def verify_service(self) -> VerifyV2ServiceContext:
        if self._verify_service is None:
            self._verify_service = get_default_verify_service(self.client)
        return self._verify_service

    def send_otp(self, to: str) -> VerificationInstance:
        return self.verify_service.verifications.create(
            to=to,
            channel="sms")

    def verify_otp(self, verification_sid: str, code: str) -> bool:
        response = self.verify_service.verification_checks.create(
            code=code,
            verification_sid=verification_sid)
        return response.valid


twilio = Twilio()
