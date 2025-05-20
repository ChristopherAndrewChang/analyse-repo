from __future__ import annotations
from typing import TYPE_CHECKING

import logging
import traceback

from django.db import models

from django.contrib.postgres.fields import ArrayField
from django.core.mail.message import EmailMultiAlternatives
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from esl_core.serialization import pack_data, unpack_data

from mailer.signals import send_email

if TYPE_CHECKING:
    from typing import Type

    from .message_template import MessageTemplate
    from .sender import Sender
    from .template import Template
    from .queue_alternative import QueueAlternative


logger = logging.getLogger(__name__)
__all__ = (
    "MessageQueueQuerySet",
    "MessageQueueManager",
    "MessageQueue",
)


class MessageQueueQuerySet(models.QuerySet):
    def create_from_message_template(
            self, message_template: MessageTemplate,
            include_alternatives: bool = False,
            context_map: dict = None,
            **kwargs) -> MessageQueue:
        data = message_template.as_queue_data()
        data.update(kwargs)
        instance = self.create(**data)
        if include_alternatives:
            instance.alt_from_message_template(
                message_template, context_map)
        return instance

    def create(self, context: dict = None, **kwargs) -> MessageQueue:
        if context:
            context = pack_data(context)
        else:
            context = None
        return super(MessageQueueQuerySet, self).create(
            context=context,
            **kwargs)


_MessageQueueManagerBase = models.Manager.from_queryset(
    MessageQueueQuerySet
)  # type: Type[MessageQueueQuerySet]


class MessageQueueManager(_MessageQueueManagerBase):
    pass


class MessageQueue(models.Model):
    sender_id: int
    sender = models.ForeignKey(
        "mailer.Sender", on_delete=models.CASCADE,
        verbose_name=_("sender"),
        null=True, blank=True)  # type: Sender

    # RFC 2822: Maximum length of subject is 998 characters
    subject = models.CharField(
        _("subject"), max_length=256, blank=True)

    context = models.BinaryField(
        _("context"), null=True, blank=True)

    body_template_id: int
    body_template = models.ForeignKey(
        "mailer.Template", on_delete=models.CASCADE,
        verbose_name=_("body template"),
        blank=True, null=True)  # type: Template
    body_str = models.TextField(
        _("body str"), null=True, blank=True)

    from_email = models.EmailField(
        _("from email"), null=True, blank=True)
    to = ArrayField(
        models.EmailField(), verbose_name=_("to"))
    cc = ArrayField(
        models.EmailField(), verbose_name=_("cc"),
        null=True, blank=True)
    bcc = ArrayField(
        models.EmailField(), verbose_name=_("bcc"),
        null=True, blank=True)
    reply_to = ArrayField(
        models.EmailField(), verbose_name=_("reply to"),
        null=True, blank=True)

    created = models.DateTimeField(
        _("created time"), auto_now_add=True,
        editable=False)
    executed = models.DateTimeField(
        _("executed time"),
        null=True, blank=True, editable=False)
    finished = models.DateTimeField(
        _("finished time"),
        null=True, blank=True, editable=False)
    exception = models.TextField(
        _("exception stack"),
        null=True, blank=True, editable=False)

    objects = MessageQueueManager()

    def unpack_context(self) -> dict | None:
        if (context := self.context) is not None:
            return unpack_data(context)
        return None

    def alt_from_message_template(
            self, instance: MessageTemplate,
            context_map: dict = None):
        if not context_map:
            context_map = {}

        for template in instance.alternatives.all():  # type: Template
            # noinspection PyUnresolvedReferences
            self.alternatives.create(
                template=template,
                context=context_map.get(template.code, None)
            )

    def build_message(self) -> EmailMultiAlternatives:
        context = self.unpack_context() or {}
        if self.body_template_id:
            body = self.body_template.render(context)
        elif (body := self.body_str) is not None:
            pass
        else:
            body = ""

        message = EmailMultiAlternatives(
            self.subject,
            body,
            from_email=self.from_email,
            to=self.to,
            cc=self.cc,
            bcc=self.bcc,
            reply_to=self.reply_to,
        )
        for alt in self.alternatives.all():  # type: QueueAlternative
            alt.attach(message, context)
        return message

    def send_async(
            self, *, sender: Sender = None,
            fail_silently: bool = False,
            task_kwargs: dict = None):
        send_email.send(
            sender=self.__class__, instance=self,
            mail_sender=sender, fail_silently=fail_silently,
            task_kwargs=task_kwargs)

    def send(
            self, *, sender: Sender = None,
            fail_silently: bool = False, save: bool = True):
        if self.executed:
            raise TypeError("already executed")

        sender = sender or self.sender
        if not sender:
            raise ValueError("sender is empty")

        exc = None
        self.executed = timezone.now()
        try:
            sender.send_messages([self], fail_silently=fail_silently)
        except Exception as e:
            exc = e
            self.exception = traceback.format_exc()
        finally:
            self.finished = timezone.now()
        if save:
            self.save(update_fields=["executed", "exception", "finished"])
        if exc:
            raise exc
