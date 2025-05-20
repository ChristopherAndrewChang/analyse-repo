from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models

from django.utils.translation import gettext_lazy as _

from esl_core.serialization import pack_data, unpack_data

if TYPE_CHECKING:
    from typing import Type
    from django.core.mail.message import EmailMultiAlternatives
    from .template import Template
    from .message_queue import MessageQueue


logger = logging.getLogger(__name__)
__all__ = (
    "QueueAlternativeQuerySet",
    "QueueAlternativeManager",
    "QueueAlternative",
)


class QueueAlternativeQuerySet(models.QuerySet):
    def create(self, context: dict = None, **kwargs) -> QueueAlternative:
        if context:
            context = pack_data(context)
        else:
            context = None
        return super(QueueAlternativeQuerySet, self).create(
            context=context, **kwargs)


_QueueAlternativeManagerBase = models.Manager.from_queryset(
    QueueAlternativeQuerySet
)  # type: Type[QueueAlternativeQuerySet]


class QueueAlternativeManager(_QueueAlternativeManagerBase):
    pass


class QueueAlternative(models.Model):
    queue_id: int
    queue = models.ForeignKey(
        "mailer.MessageQueue", on_delete=models.CASCADE,
        related_name="alternatives",
        verbose_name=_("queue"))  # type: MessageQueue
    template_id: int
    template = models.ForeignKey(
        "mailer.Template", on_delete=models.CASCADE,
        verbose_name=_("body template"))  # type: Template
    context = models.BinaryField(
        _("context"), null=True, blank=True)

    objects = QueueAlternativeManager()

    class Meta:
        unique_together = ("queue", "template")

    def unpack_context(self) -> dict | None:
        if (context := self.context) is not None:
            return unpack_data(context)
        return None

    def attach(self, msg: EmailMultiAlternatives, queue_context: dict):
        context = self.unpack_context() or queue_context
        msg.attach_alternative(
            self.template.render(context),
            self.template.mimetype)
