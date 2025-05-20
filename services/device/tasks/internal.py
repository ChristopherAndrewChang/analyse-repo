from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from celery import current_app as celery_app

from device.models import Device, DeviceHistory
from device.tasks import constants

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = ("device_create_history_task",)


@celery_app.task(
    name=constants.TASK_DEVICE_CREATE_HISTORY,
    queue=constants.QUEUE_INTERNAL,
    shared=False)
def device_create_history_task(obj_id: int):
    device = Device.objects.get(id=obj_id)
    DeviceHistory.objects.create_from_device(device)
