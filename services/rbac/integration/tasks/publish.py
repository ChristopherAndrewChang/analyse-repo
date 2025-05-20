from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from idvalid_integration.tasks import (
    rbac as rbac_tasks,
)
from idvalid_integration.protos.models import (
    rbac_pb2,
)

if TYPE_CHECKING:
    from celery import Celery
    from rbac.models import RoleUser


logger = logging.getLogger(__name__)
__all__ = (
    "call_publish_role_user_create",
    "call_publish_role_user_delete",
)


def call_publish_role_user_create(
        instance: RoleUser, *,
        app: Celery = None,
        **task_opts):
    message = rbac_pb2.RoleUser(
        tenant_id=instance.role.tenant_id,
        role_id=instance.role_id,
        user_id=instance.user_id)
    return rbac_tasks.publish_role_user_create(
        message, app=app, **task_opts)


def call_publish_role_user_delete(
        tenant_id: int, role_id: int, user_id: int, *,
        app: Celery = None,
        **task_opts):
    message = rbac_pb2.RoleUser(
        tenant_id=tenant_id,
        role_id=role_id,
        user_id=user_id)
    return rbac_tasks.publish_role_user_delete(
        message, app=app, **task_opts)
