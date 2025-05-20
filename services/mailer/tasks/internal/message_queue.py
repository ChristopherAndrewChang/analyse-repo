from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from celery import current_app

from django.db.models.query import Prefetch

from mailer.models import (
    Sender,
    MessageQueue,
    QueueAlternative)

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = ("message_queue_send_mail_task", )


@current_app.task(
    name="esl.mailer.message_queue.int.send",
    queue="mailer",
    shared=False)
def message_queue_send_mail_task(
        queue_id: int, *,
        sender_id: int = None,
        fail_silently: bool = False):
    if sender_id:
        sender = Sender.objects.get(pk=sender_id)
    else:
        sender = None

    queue = MessageQueue.objects.select_related(
        "sender", "body_template"
    ).prefetch_related(
        Prefetch(
            "alternatives",
            queryset=QueueAlternative.objects.select_related(
                "template"
            )
        ),
        "attachments"
    ).get(pk=queue_id)  # type: MessageQueue

    # try:
    queue.send(sender=sender, fail_silently=fail_silently)
    # except Exception as e:
    #     raise e
    #     return {"status": "FAILED", "message": str(e)}
    # else:
    #     # instance.delete()
    #     return {"status": "OK"}
    return {
        "message_queue_id": queue_id,
        "sender_id": sender_id,
    }
