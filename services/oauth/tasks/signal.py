from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from celery import current_app as celery_app

from oauth.models import (
    PromptRequest,
)
from oauth.tasks import constants

if TYPE_CHECKING:
    from celery import Task


logger = logging.getLogger(__name__)
__all__ = (

)


@celery_app.task(
    name=constants.TASK_SIGNAL_PROMPT_REQUEST_POST_ANSWER,
    queue=constants.QUEUE_SIGNAL,
    shared=False)
def signal_prompt_request_post_answer_task(pk: int):
    instance = PromptRequest.objects.select_related(
        "application").get(pk=pk)  # type: PromptRequest
    instance.notify_callback()
