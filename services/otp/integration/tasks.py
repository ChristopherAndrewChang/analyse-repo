from __future__ import annotations
from typing import TYPE_CHECKING

import logging

# from celery import current_app

from idvalid_integration.tasks import (
    call_task,
    otp as otp_tasks,
)
from idvalid_integration.protos.models import otp_pb2

from otp.tasks import constants

if TYPE_CHECKING:
    from celery import Celery
    # from celery.result import AsyncResult

    from otp.models import (
        # Code,
        Otp,
    )


logger = logging.getLogger(__name__)
__all__ = (
    "call_publish_otp",
    "call_signal_otp_post_create",
    "call_signal_otp_apply",

)


# def call_code_post_create(code: Code):
#     return current_app.send_task(
#         constants.TASK_SIGNAL_CODE_POST_CREATE,
#         args=(code.pk,),
#         exchange=constants.EXCHANGE_OTP,
#         routing_key=constants.ROUTING_SIGNAL)


def call_publish_otp(
        instance: Otp, *,
        app: Celery = None,
        **task_opts):
    message = otp_pb2.Otp(
        id=instance.subid,
        object_id=instance.object_id,
        usage=instance.usage,
        ref_id=instance.ref_id,
        token=instance.token,
        applied=instance.applied)
    message.expires.FromDatetime(instance.expires)
    message.applied_time.FromDatetime(instance.applied_time)
    message.created.FromDatetime(instance.created)
    return otp_tasks.publish(
        message, instance.usage,
        app=app, **task_opts)


def call_signal_otp_post_create(
        instance: Otp, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_SIGNAL_OTP_POST_CREATE,
        app=app,
        args=(instance.pk,),
        exchange=constants.EXCHANGE,
        routing_key=constants.ROUTING_SIGNAL,
        **task_opts)


def call_signal_otp_apply(
        instance: Otp, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_SIGNAL_OTP_APPLY,
        app=app,
        args=(instance.pk,),
        exchange=constants.EXCHANGE,
        routing_key=constants.ROUTING_SIGNAL,
        **task_opts)
