from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db.models.query import Prefetch

from common.celery import shared_task

from mailer.models import (
    Sender,
    MessageQueue,
    QueueAlternative)

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = ("send_mail_task", )


@shared_task
def send_mail_task(
        queue_id: int,
        sender_id: int = None,
        fail_silently: bool = False) -> dict:
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

    try:
        queue.send(sender=sender, fail_silently=fail_silently)
    except Exception as e:
        raise e
        return {"status": "FAILED", "message": str(e)}
    else:
        # instance.delete()
        return {"status": "OK"}

