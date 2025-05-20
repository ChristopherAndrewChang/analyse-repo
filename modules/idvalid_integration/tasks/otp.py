from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from idvalid_integration.tasks import constants, call_task

from .utils import validate_routing_part

if TYPE_CHECKING:
    from celery import Celery
    from idvalid_integration.protos.models import otp_pb2


logger = logging.getLogger(__name__)
__all__ = (
    "create",
    "publish",
    # "apply",
)


def create(message: otp_pb2.CreateOtp, *,
           app: Celery = None,
           **task_opts):
    return call_task(
        constants.TASK_EXTERNAL_OTP_CREATE,
        app=app,
        args=(message.SerializeToString(deterministic=True),),
        argsrepr="otp.CreateOtp message",
        exchange=constants.EXCHANGE_OTP,
        routing_key=constants.ROUTING_OTP_EXTERNAL,
        **task_opts)


def publish(message: otp_pb2.Otp,
            event: str, *,
            app: Celery = None,
            **task_opts):
    validate_routing_part(event)
    return call_task(
        constants.TASK_CONSUME_OTP_PUBLISH,
        app=app,
        args=(message.SerializeToString(deterministic=True),),
        argsrepr="otp.Otp message",
        exchange=constants.EXCHANGE_PUBLISHER,
        routing_key=f"{constants.ROUTING_OTP_PUBLISH_PREFIX}.{event}",
        **task_opts)


# def apply(message: otp_pb2.Otp,
#           event: str, *,
#           app: Celery = None,
#           **task_opts):
#     validate_routing_part(event)
#     return call_task(
#         constants.TASK_CONSUME_OTP_APPLY,
#         app=app,
#         args=(message.SerializeToString(deterministic=True),),
#         argsrepr="otp.Otp message",
#         exchange=constants.EXCHANGE_PUBLISHER,
#         routing_key=f"{constants.ROUTING_OTP_APPLY_PREFIX}.{event}",
#         **task_opts)
