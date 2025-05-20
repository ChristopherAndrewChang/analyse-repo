from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from celery import current_app as celery_app

from idvalid_integration.protos.models import otp_pb2

from account.models import Enrollment
from account.tasks import constants

if TYPE_CHECKING:
    from celery import Task


logger = logging.getLogger(__name__)
__all__ = (
    "consume_otp_publish_task",
)


@celery_app.task(
    name=constants.TASK_CONSUME_OTP_PUBLISH,
    queue=constants.QUEUE_CONSUME,
    shared=False)
def consume_otp_publish_task(message: bytes):
    message = otp_pb2.Otp.FromString(message)
    instance = Enrollment.objects.get(
        subid=message.object_id)  # type: Enrollment
    instance.setup_token(
        message.id, message.token)
