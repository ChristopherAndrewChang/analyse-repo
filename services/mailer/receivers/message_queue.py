from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from celery import current_app

from django.dispatch.dispatcher import receiver

from mailer.models import MessageQueue
from mailer.signals import send_email
# from mailer.tasks import send_mail_task

if TYPE_CHECKING:
    from mailer.models import Sender


logger = logging.getLogger(__name__)
__all__ = ("on_send_email", )


@receiver(send_email, sender=MessageQueue)
def on_send_email(
        instance: MessageQueue, mail_sender: Sender,
        fail_silently: bool, **kwargs):
    current_app.send_task(
        "esl.mailer.message_queue.int.send",
        args=(instance.pk,),
        kwargs={
            "sender_id": mail_sender.pk if mail_sender else None,
            "fail_silently": fail_silently
        },
        exchange="esl",
        routing_key="mailer.internal",
        **(kwargs.get("task_kwargs", None) or {})
    )

    # send_mail_task.delay(
    #     queue_id=instance.pk,
    #     sender_id=mail_sender.pk if mail_sender else None,
    #     fail_silently=fail_silently)
