from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from idvalid_integration.tasks import constants, call_task

if TYPE_CHECKING:
    from celery import Celery
    from idvalid_integration.protos.models import enrollment_pb2


logger = logging.getLogger(__name__)
__all__ = ("publish",)


def publish(message: enrollment_pb2.Enrollment, *,
            app: Celery = None,
            **task_opts):
    return call_task(
        constants.TASK_CONSUME_ENROLLMENT_PUBLISH,
        app=app,
        args=(message.SerializeToString(deterministic=True),),
        argsrepr="enrollment_pb2.Enrollment message",
        exchange=constants.EXCHANGE_PUBLISHER,
        routing_key=constants.ROUTING_ENROLLMENT,
        **task_opts)
