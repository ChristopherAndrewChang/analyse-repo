from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from celery import current_app as celery_app

from rbac.models import (
    RoleUser,
    Role,
)
from rbac.tasks import constants
from rbac.integration import tasks

if TYPE_CHECKING:
    from celery import Task


logger = logging.getLogger(__name__)
__all__ = (
    "signal_role_user_post_create_task",
    "signal_role_user_post_delete_task",
)


@celery_app.task(
    name=constants.TASK_SIGNAL_ROLE_USER_POST_CREATE,
    queue=constants.QUEUE_SIGNAL,
    shared=False,
    bind=True)
def signal_role_user_post_create_task(
        self: Task, role_id: int, user_id: int):
    instance = RoleUser.objects.get(role_id=role_id, user_id=user_id)
    tasks.call_publish_role_user_create(instance, app=self._app)


@celery_app.task(
    name=constants.TASK_SIGNAL_ROLE_USER_POST_DELETE,
    queue=constants.QUEUE_SIGNAL,
    shared=False,
    bind=True)
def signal_role_user_post_delete_task(
        self: Task, role_id: int, user_id: int):
    role = Role.objects.get(pk=role_id)  # type: Role
    tasks.call_publish_role_user_delete(
        tenant_id=role.tenant_id, role_id=role_id,
        user_id=user_id, app=self._app)
