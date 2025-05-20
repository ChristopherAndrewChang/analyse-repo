from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from celery import current_app as celery_app

from idvalid_integration.protos.models import authn_pb2

from device.models import Platform, Device
from device.tasks import constants

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "consume_auth_platform_create_task",
    "consume_auth_platform_update_task",
    "consume_auth_platform_delete_task",

    "consume_auth_user_logged_in_task",

    "consume_auth_session_delete_task",
)


@celery_app.task(
    name=constants.TASK_CONSUME_AUTH_PLATFORM_CREATE,
    queue=constants.QUEUE_CONSUME,
    shared=False)
def consume_auth_platform_create_task(message: bytes):
    message = authn_pb2.Platform.FromString(message)
    Platform.objects.create_or_update_from_message(message)


@celery_app.task(
    name=constants.TASK_CONSUME_AUTH_PLATFORM_UPDATE,
    queue=constants.QUEUE_CONSUME,
    shared=False)
def consume_auth_platform_update_task(message: bytes):
    message = authn_pb2.Platform.FromString(message)
    Platform.objects.create_or_update_from_message(message)


@celery_app.task(
    name=constants.TASK_CONSUME_AUTH_PLATFORM_DELETE,
    queue=constants.QUEUE_CONSUME,
    shared=False)
def consume_auth_platform_delete_task(message: bytes):
    message = authn_pb2.Platform.FromString(message)
    Platform.objects.filter(pk=message.id).delete()


@celery_app.task(
    name=constants.TASK_CONSUME_AUTH_USER_LOGGED_IN,
    queue=constants.QUEUE_CONSUME,
    shared=False)
def consume_auth_user_logged_in_task(message: bytes):
    message = authn_pb2.UserLoggedIn.FromString(message)
    device = Device.objects.create_from_message(message)
    device.create_history()


@celery_app.task(
    name=constants.TASK_CONSUME_AUTH_SESSION_DELETE,
    queue=constants.QUEUE_CONSUME,
    shared=False)
def consume_auth_session_delete_task(message: bytes):
    message = authn_pb2.Session.FromString(message)
    Device.objects.filter(session_id=message.id).delete()
