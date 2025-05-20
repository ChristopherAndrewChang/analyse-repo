from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from celery import current_app as celery_app

from tenant.models import (
    Tenant,
    TenantUser,
)
from tenant.tasks import constants
from tenant.integration import tasks

if TYPE_CHECKING:
    from celery import Task


logger = logging.getLogger(__name__)
__all__ = (
    "signal_tenant_post_save_task",
    "signal_tenant_user_post_save_task",
    "signal_tenant_user_post_delete_task",
)


@celery_app.task(
    name=constants.TASK_SIGNAL_TENANT_POST_SAVE,
    queue=constants.QUEUE_SIGNAL,
    shared=False,
    bind=True)
def signal_tenant_post_save_task(
        self: Task, tenant_id: int):
    instance = Tenant.objects.get(pk=tenant_id)
    tasks.call_publish_tenant(instance, app=self._app)


@celery_app.task(
    name=constants.TASK_SIGNAL_TENANT_USER_POST_SAVE,
    queue=constants.QUEUE_SIGNAL,
    shared=False,
    bind=True)
def signal_tenant_user_post_save_task(
        self: Task, tenant_id: int, user_id: int):
    instance = TenantUser.objects.get(tenant_id=tenant_id, user_id=user_id)
    tasks.call_publish_tenant_user(
        instance, app=self._app)


@celery_app.task(
    name=constants.TASK_SIGNAL_TENANT_USER_POST_DELETE,
    queue=constants.QUEUE_SIGNAL,
    shared=False,
    bind=True)
def signal_tenant_user_post_delete_task(
        self: Task, tenant_id: int, user_id: int):
    tasks.call_publish_tenant_user_delete(
        tenant_id, user_id, app=self._app)
