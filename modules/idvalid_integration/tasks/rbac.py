from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from idvalid_integration.tasks import constants, call_task

if TYPE_CHECKING:
    from celery import Celery
    from idvalid_integration.protos.models import rbac_pb2


logger = logging.getLogger(__name__)
__all__ = (
    "publish_role_user_create",
    "publish_role_user_delete",
)


def publish_role_user_create(
        message: rbac_pb2.RoleUser, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_CONSUME_RBAC_ROLE_USER_CREATE,
        app=app,
        args=(message.SerializeToString(deterministic=True),),
        argsrepr="rbac_pb2.RoleUser message",
        exchange=constants.EXCHANGE_PUBLISHER,
        routing_key=f"{constants.ROUTING_RBAC_ROLE_USER_PUBLISH_PREFIX}.create",
        **task_opts)


def publish_role_user_delete(
        message: rbac_pb2.RoleUser, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_CONSUME_RBAC_ROLE_USER_DELETE,
        app=app,
        args=(message.SerializeToString(deterministic=True),),
        argsrepr="rbac_pb2.RoleUser message",
        exchange=constants.EXCHANGE_PUBLISHER,
        routing_key=f"{constants.ROUTING_RBAC_ROLE_USER_PUBLISH_PREFIX}.delete",
        **task_opts)
