from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import transaction
from django.dispatch import receiver

from oauth.integration import tasks
from oauth.models import (
    PromptRequest,
)
from oauth.signals import post_answer

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "on_prompt_request_post_answer",
)


@receiver(post_answer, sender=PromptRequest)
def on_prompt_request_post_answer(instance: PromptRequest, **kwargs):
    def call_task():
        tasks.call_signal_prompt_request_post_answer(instance)

    # noinspection PyProtectedMember
    transaction.on_commit(call_task, using=instance._state.db)
