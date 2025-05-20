from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from idvalid_integration.tasks import constants, call_task

if TYPE_CHECKING:
    from celery import Celery
    from idvalid_integration.protos.models import tenant_pb2


logger = logging.getLogger(__name__)
__all__ = (
    "publish_tenant",
    "publish_tenant_user",
    "publish_tenant_user_delete",
)


def publish_tenant(
        message: tenant_pb2.Tenant, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_CONSUME_TENANT_PUBLISH,
        app=app,
        args=(message.SerializeToString(deterministic=True),),
        argsrepr="tenant_pb2.Tenant message",
        exchange=constants.EXCHANGE_PUBLISHER,
        routing_key=f"{constants.ROUTING_TENANT_PUBLISH_PREFIX}",
        **task_opts)


def publish_tenant_user(
        message: tenant_pb2.TenantUser, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_CONSUME_TENANT_USER_PUBLISH,
        app=app,
        args=(message.SerializeToString(deterministic=True),),
        argsrepr="tenant_pb2.TenantUser message",
        exchange=constants.EXCHANGE_PUBLISHER,
        routing_key=f"{constants.ROUTING_TENANT_USER_PUBLISH_PREFIX}",
        **task_opts)


def publish_tenant_user_delete(
        message: tenant_pb2.TenantUser, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_CONSUME_TENANT_USER_DELETE,
        app=app,
        args=(message.SerializeToString(deterministic=True),),
        argsrepr="tenant_pb2.TenantUser message",
        exchange=constants.EXCHANGE_PUBLISHER,
        routing_key=f"{constants.ROUTING_TENANT_USER_PUBLISH_PREFIX}.delete",
        **task_opts)
