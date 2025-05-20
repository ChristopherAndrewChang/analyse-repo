from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from celery import current_app as celery_app

from device.tasks import constants
from device.models import DeviceHistory, Device
from device.integration import tasks

if TYPE_CHECKING:
    from celery import Task


logger = logging.getLogger(__name__)
__all__ = ("signal_device_post_delete_task",)


@celery_app.task(
    name=constants.TASK_SIGNAL_DEVICE_POST_DELETE,
    queue=constants.QUEUE_SIGNAL,
    shared=False)
def signal_device_post_delete_task(user_id: int, device_id: int):
    DeviceHistory.objects.filter(
        user_id=user_id,
        device_id=device_id,
    ).revoke()
    tasks.call_publish_device_delete(user_id, device_id)


@celery_app.task(
    name=constants.TASK_SIGNAL_DEVICE_POST_REVOKE,
    queue=constants.QUEUE_SIGNAL,
    shared=False,
    bind=True)
def signal_device_post_revoke_task(self: Task, device_id: int):
    instance = Device.objects.get(pk=device_id)
    tasks.call_external_auth_session_revoke(instance, app=self._app)
