from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from idvalid_integration.tasks import (
    call_task,
    enrollment as enrollment_tasks,
    otp as otp_tasks,
)
from idvalid_integration.protos.models import (
    enrollment_pb2,
    otp_pb2
)

from enrollment.tasks import constants

if TYPE_CHECKING:
    from celery import Celery
    from enrollment.models import Code

logger = logging.getLogger(__name__)
__all__ = (
    "call_publish_enrollment",
    "call_signal_code_post_create",
    "call_signal_code_post_apply",
    "call_external_otp_create",
)


def call_publish_enrollment(
        instance: Code, *,
        app: Celery = None,
        **task_opts):
    message = enrollment_pb2.Enrollment(
        id=instance.subid,
        state=instance.state,
        device_id=instance.device_id,
        user_agent=instance.user_agent)
    message.created.FromDatetime(instance.created)
    email_instance = instance.email
    email_message = message.email
    email_message.id = email_instance.subid
    email_message.email = email_instance.email
    email_message.is_registered = email_instance.is_registered
    if email_instance.registered_date:
        email_message.registered_date.FromDatetime(
            email_instance.registered_date)
    email_message.created.FromDatetime(email_instance.created)
    return enrollment_tasks.publish(
        message, app=app, **task_opts)


def call_signal_code_post_create(
        instance: Code, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_SIGNAL_CODE_POST_CREATE,
        app=app,
        args=(instance.pk,),
        exchange=constants.EXCHANGE,
        routing_key=constants.ROUTING_SIGNAL,
        **task_opts)


def call_signal_code_post_apply(
        instance: Code, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_SIGNAL_CODE_POST_APPLY,
        app=app,
        args=(instance.pk,),
        exchange=constants.EXCHANGE,
        routing_key=constants.ROUTING_SIGNAL,
        **task_opts)


def call_external_otp_create(
        instance: Code, *,
        app: Celery = None,
        **task_opts):
    message = otp_pb2.CreateOtp(
        object_id=instance.subid,
        usage=constants.OTP_USAGE,
        ref_id=instance.email.subid,
        method=otp_pb2.Method.METHOD_MAIL,
        device_id=instance.device_id,
        user_agent=instance.user_agent,
        email_address=instance.email.email)
    return otp_tasks.create(
        message, app=app, **task_opts)
