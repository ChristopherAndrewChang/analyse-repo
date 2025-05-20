from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from celery import current_app as celery_app

from idvalid_integration.protos.models import otp_pb2

from enrollment.models import Code
from enrollment.tasks import constants

if TYPE_CHECKING:
    from celery import Task


logger = logging.getLogger(__name__)
__all__ = (
    "consume_otp_publish_task",
    "consume_otp_apply_task",
)


@celery_app.task(
    name=constants.TASK_CONSUME_OTP_PUBLISH,
    queue=constants.QUEUE_CONSUME,
    shared=False,
    bind=True)
def consume_otp_publish_task(self: Task, message: bytes):
    message = otp_pb2.Otp.FromString(message)
    instance = Code.objects.get(subid=message.object_id)


@celery_app.task(
    name=constants.TASK_CONSUME_OTP_APPLY,
    queue=constants.QUEUE_CONSUME,
    shared=False,
    bind=True)
def consume_otp_apply_task(self: Task, message: bytes):
    message = otp_pb2.Otp.FromString(message)
    instance = Code.objects.get(subid=message.object_id)
