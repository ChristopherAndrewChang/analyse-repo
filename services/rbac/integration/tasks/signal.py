from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from idvalid_integration.tasks import call_task

from rbac.tasks import constants

if TYPE_CHECKING:
    from celery import Celery
    from rbac.models import (
        RoleUser,
    )


logger = logging.getLogger(__name__)
__all__ = (
    "call_signal_role_user_post_create",
    "call_signal_role_user_post_delete",
)


def call_signal_role_user_post_create(
        instance: RoleUser, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_SIGNAL_ROLE_USER_POST_CREATE,
        app=app,
        args=(instance.role_id, instance.user_id),
        exchange=constants.EXCHANGE,
        routing_key=constants.ROUTING_SIGNAL,
        **task_opts)


def call_signal_role_user_post_delete(
        instance: RoleUser, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_SIGNAL_ROLE_USER_POST_DELETE,
        app=app,
        args=(instance.role_id, instance.user_id),
        exchange=constants.EXCHANGE,
        routing_key=constants.ROUTING_SIGNAL,
        **task_opts)
