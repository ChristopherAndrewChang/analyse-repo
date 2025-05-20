from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from celery import current_app as celery_app

from account.models import Enrollment
from account.tasks import constants
from account.integration import tasks

if TYPE_CHECKING:
    from celery import Task


logger = logging.getLogger(__name__)
__all__ = (
    "signal_enrollment_post_create_task",
)


@celery_app.task(
    name=constants.TASK_SIGNAL_ENROLLMENT_POST_CREATE,
    queue=constants.QUEUE_SIGNAL,
    shared=False,
    bind=True)
def signal_enrollment_post_create_task(self: Task, pk: int):
    instance = Enrollment.objects.select_related(
        "email").get(pk=pk)  # type: Enrollment
    Enrollment.objects.exclude(
        pk=pk
    ).suppress(instance.email)
    tasks.call_external_otp_create(instance, app=self._app)
