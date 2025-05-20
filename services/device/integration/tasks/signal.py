from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from idvalid_integration.tasks import call_task

from device.tasks import constants

if TYPE_CHECKING:
    from celery import Celery

    from device.models import Device


logger = logging.getLogger(__name__)
__all__ = (
    "call_signal_device_post_delete",
    "call_signal_device_post_revoke",
)


def call_signal_device_post_delete(
        device: Device, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_SIGNAL_DEVICE_POST_DELETE,
        app=app,
        args=(device.user_id, device.device_id),
        exchange=constants.EXCHANGE,
        routing_key=constants.ROUTING_SIGNAL,
        **task_opts)


def call_signal_device_post_revoke(
        instance: Device, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_SIGNAL_DEVICE_POST_REVOKE,
        app=app,
        args=(instance.pk,),
        exchange=constants.EXCHANGE,
        routing_key=constants.ROUTING_SIGNAL,
        **task_opts)
