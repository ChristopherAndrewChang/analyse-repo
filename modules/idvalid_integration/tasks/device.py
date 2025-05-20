from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from idvalid_integration.tasks import constants, call_task

if TYPE_CHECKING:
    from celery import Celery
    from idvalid_integration.protos.models import device_pb2


logger = logging.getLogger(__name__)
__all__ = ("publish_device_delete",)


def publish_device_delete(
        message: device_pb2.Device, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_CONSUME_DEVICE_DELETE,
        app=app,
        args=(message.SerializeToString(deterministic=True),),
        argsrepr="device_pb2.Device message",
        exchange=constants.EXCHANGE_PUBLISHER,
        routing_key=f"{constants.ROUTING_DEVICE_PUBLISH_PREFIX}.revoke",
        **task_opts)
