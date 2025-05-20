from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from idvalid_integration.tasks import (
    call_task,
    otp as otp_tasks,
)
from idvalid_integration.protos.models import (
    otp_pb2,
)

from account.tasks import constants

if TYPE_CHECKING:
    from celery import Celery
    from account.models import Enrollment


logger = logging.getLogger(__name__)
__all__ = (
    "call_external_otp_create",
    "call_signal_enrollment_post_create",
)


def call_external_otp_create(
        instance: Enrollment, *,
        app: Celery = None,
        **task_opts):
    message = otp_pb2.CreateOtp(
        object_id=instance.subid,
        usage=constants.OTP_USAGE,
        ref_id=instance.email.subid,
        method=otp_pb2.Method.METHOD_MAIL,
        device_id=instance.device_id,
        user_agent=instance.user_agent,
        email_address=instance.email.address)
    return otp_tasks.create(message, app=app, **task_opts)


def call_signal_enrollment_post_create(
        instance: Enrollment, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_SIGNAL_ENROLLMENT_POST_CREATE,
        app=app,
        args=(instance.pk,),
        exchange=constants.EXCHANGE,
        routing_key=constants.ROUTING_SIGNAL,
        **task_opts)
