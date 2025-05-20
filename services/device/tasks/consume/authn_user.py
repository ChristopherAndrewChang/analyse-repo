from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from celery import current_app as celery_app

from idvalid_integration.protos.models import authn_pb2

from device.models import Device
from device.tasks import constants

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = ("consume_user_logged_in_task",)


@celery_app.task(
    name=constants.TASK_CONSUME_AUTH_USER_LOGGED_IN,
    queue=constants.QUEUE_CONSUME,
    shared=False)
def consume_user_logged_in_task(message: bytes):
    message = authn_pb2.UserLoggedIn.FromString(message)
    device = Device.objects.create_from_message(message)
    device.create_history()
