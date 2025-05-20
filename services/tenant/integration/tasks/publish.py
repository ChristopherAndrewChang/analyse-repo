from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from idvalid_integration.tasks import (
    tenant as tenant_tasks,
)
from idvalid_integration.protos.models import (
    tenant_pb2,
)

if TYPE_CHECKING:
    from celery import Celery
    from tenant.models import Tenant, TenantUser


logger = logging.getLogger(__name__)
__all__ = (
    "call_publish_tenant",
    "call_publish_tenant_user",
    "call_publish_tenant_user_delete",
)


def call_publish_tenant(
        instance: Tenant, *,
        app: Celery = None,
        **task_opts):
    message = tenant_pb2.Tenant(
        id=instance.pk,
        subid=instance.subid,
        name=instance.name,
        is_active=instance.is_active)
    return tenant_tasks.publish_tenant(
        message, app=app, **task_opts)


def call_publish_tenant_user(
        instance: TenantUser, *,
        app: Celery = None,
        **task_opts):
    message = tenant_pb2.TenantUser(
        tenant_id=instance.tenant_id,
        user_id=instance.user_id,
        is_owner=instance.is_owner,
        is_registered=instance.is_registered,
        is_active=instance.is_active)
    return tenant_tasks.publish_tenant_user(
        message, app=app, **task_opts)


def call_publish_tenant_user_delete(
        tenant_id: int, user_id: int, *,
        app: Celery = None,
        **task_opts):
    message = tenant_pb2.TenantUser(
        tenant_id=tenant_id,
        user_id=user_id)
    return tenant_tasks.publish_tenant_user_delete(
        message, app=app, **task_opts)
