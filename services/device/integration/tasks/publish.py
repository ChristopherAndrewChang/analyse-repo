from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from idvalid_integration.tasks import device as device_tasks
from idvalid_integration.protos.models import device_pb2


if TYPE_CHECKING:
    from celery import Celery


logger = logging.getLogger(__name__)
__all__ = ("call_publish_device_delete",)


def call_publish_device_delete(
        user_id: int, device_id: str,
        app: Celery = None,
        **task_opts):
    message = device_pb2.Device(user_id=user_id, device_id=device_id)
    return device_tasks.publish_device_delete(
        message=message,
        app=app, **task_opts)
