from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.core.mail import send_mail

from celery import current_app

from otp.integration import tasks
from otp.models import Otp, Recipient2
from otp.tasks import constants
from otp.twilio import twilio

if TYPE_CHECKING:
    from celery import Celery, Task


logger = logging.getLogger(__name__)
__all__ = (
    # "signal_code_post_create_task",
    "signal_otp_post_create_task",
    "signal_otp_apply_task",
)


# @current_app.task(
#     name=constants.TASK_SIGNAL_CODE_POST_CREATE,
#     queue=constants.QUEUE_SIGNAL,
#     shared=False)
# def signal_code_post_create_task(code_id: int):
#     code = Code.objects.get(pk=code_id)  # type: Code
#     print(code.prepare_code())


@current_app.task(
    name=constants.TASK_SIGNAL_OTP_POST_CREATE,
    queue=constants.QUEUE_SIGNAL,
    shared=False,
    bind=True)
def signal_otp_post_create_task(self: Task, instance_id: int):
    instance = Otp.objects.select_related(
        "recipient"
    ).get(pk=instance_id)  # type: Otp
    # suppress old otp
    Otp.objects.filter(
        usage=instance.usage
    ).exclude(
        pk=instance_id
    ).suppress(
        instance.ref_id)

    # generate pin
    instance.send()

    # publish otp
    # tasks.call_publish_otp(instance, app=self._app)


@current_app.task(
    name=constants.TASK_SIGNAL_OTP_APPLY,
    queue=constants.QUEUE_SIGNAL,
    shared=False,
    bind=True)
def signal_otp_apply_task(self: Task, instance_id: int):
    instance = Otp.objects.applied().get(pk=instance_id)  # type: Otp
    tasks.call_publish_otp(instance, app=self._app)
