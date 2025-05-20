from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from celery import current_app as celery_app

from enrollment.models import Code
from enrollment.tasks import constants
from enrollment.integration import tasks

if TYPE_CHECKING:
    from celery import Task


logger = logging.getLogger(__name__)
__all__ = (
    "signal_code_post_create_task",
    "signal_code_post_apply_task",
)


@celery_app.task(
    name=constants.TASK_SIGNAL_CODE_POST_CREATE,
    queue=constants.QUEUE_SIGNAL,
    shared=False,
    bind=True)
def signal_code_post_create_task(self: Task, pk: int):
    instance = Code.objects.select_related(
        "email").get(pk=pk)  # type: Code
    tasks.call_publish_enrollment(instance, app=self._app)
    tasks.call_external_otp_create(instance, app=self._app)


@celery_app.task(
    name=constants.TASK_SIGNAL_CODE_POST_APPLY,
    queue=constants.QUEUE_SIGNAL,
    shared=False,
    bind=True)
def signal_code_post_apply_task(self: Task, pk: int):
    pass
