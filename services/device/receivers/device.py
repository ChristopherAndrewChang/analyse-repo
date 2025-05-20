from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import transaction
# from django.db.models.signals import post_delete
from django.dispatch import receiver

from idvalid_integration.tasks import call_task

from device.models import Device
from device.integration import tasks
from device.tasks import constants
from device.signals import device_create_history, device_post_revoke

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    # "on_device_post_delete",
    "on_device_create_history",
    "on_device_post_remove",
)


# @receiver(post_delete, sender=Device)
# def on_device_post_delete(instance: Device, using: str, **kwargs):
#     def call_task():
#         tasks.call_signal_device_post_delete(instance)
#     transaction.on_commit(call_task, using=using)


@receiver(device_create_history, sender=Device)
def on_device_create_history(instance: Device, **kwargs):
    call_task(
        constants.TASK_DEVICE_CREATE_HISTORY,
        args=(instance.id, ),
        exchange=constants.EXCHANGE,
        routing_key=constants.QUEUE_INTERNAL)


@receiver(device_post_revoke, sender=Device)
def on_device_post_remove(instance: Device, using: str, **kwargs):
    def call_task():
        tasks.call_signal_device_post_revoke(instance)
    transaction.on_commit(call_task, using=using)
