from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from celery import current_app as celery_app

from idvalid_integration.protos.models import otp_pb2

from otp.models import Otp
from otp.tasks import constants

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "external_otp_create_task",
)


@celery_app.task(
    name=constants.TASK_EXTERNAL_OTP_CREATE,
    queue=constants.QUEUE_EXTERNAL,
    shared=False)
def external_otp_create_task(message: bytes):
    instance = Otp.objects.create_from_message(
        otp_pb2.CreateOtp.FromString(message))
    return instance.subid
