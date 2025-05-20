from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from idvalid_integration.tasks import call_task

from oauth.tasks import constants

if TYPE_CHECKING:
    from celery import Celery
    from oauth.models import (
        PromptRequest,
    )


logger = logging.getLogger(__name__)
__all__ = (
    "call_signal_prompt_request_post_answer",
)


def call_signal_prompt_request_post_answer(
        instance: PromptRequest, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_SIGNAL_PROMPT_REQUEST_POST_ANSWER,
        app=app,
        args=(instance.pk,),
        exchange=constants.EXCHANGE,
        routing_key=constants.ROUTING_SIGNAL,
        **task_opts)
