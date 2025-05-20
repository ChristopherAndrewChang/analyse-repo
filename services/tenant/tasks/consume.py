from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from celery import current_app as celery_app

from idvalid_integration.protos.models import authn_pb2

from tenant.models import User
from tenant.tasks import constants

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "consume_auth_account_create_task",
    "consume_auth_user_active_flag_task",
    "consume_auth_profile_update_task",
)


@celery_app.task(
    name=constants.TASK_CONSUME_AUTH_ACCOUNT_CREATE,
    queue=constants.QUEUE_CONSUME,
    shared=False)
def consume_auth_account_create_task(message: bytes):
    message = authn_pb2.Account.FromString(message)
    User.objects.create_or_update_from_message(message)


@celery_app.task(
    name=constants.TASK_CONSUME_AUTH_USER_ACTIVE_FLAG,
    queue=constants.QUEUE_CONSUME,
    shared=False)
def consume_auth_user_active_flag_task(message: bytes):
    message = authn_pb2.UserActiveFlag.FromString(message)
    User.objects.update_active_flag_from_message(message)


@celery_app.task(
    name=constants.TASK_CONSUME_AUTH_PROFILE_UPDATE,
    queue=constants.QUEUE_CONSUME,
    shared=False)
def consume_auth_profile_update_task(message: bytes):
    message = authn_pb2.UserProfile.FromString(message)
    User.objects.update_profile_from_message(message)
