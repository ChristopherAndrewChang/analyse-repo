from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models

from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from typing import Type


logger = logging.getLogger(__name__)
__all__ = (
    "MessageTemplateQuerySet",
    "MessageTemplateManager",
    "MessageTemplate",
)


class MessageTemplateQuerySet(models.QuerySet):
    def get_by_code(
            self, code: str, *,
            include_alternatives: bool = False
    ) -> MessageTemplate:
        qs = self.select_related("sender", "body_template")
        if include_alternatives:
            qs = qs.prefetch_related("alternatives")
        return qs.get(code=code)


_MessageTemplateManagerBase = models.Manager.from_queryset(
    MessageTemplateQuerySet
)  # type: Type[MessageTemplateQuerySet]


class MessageTemplateManager(_MessageTemplateManagerBase):
    pass


class MessageTemplate(models.Model):
    code = models.CharField(
        _("name"), max_length=64, unique=True)

    # RFC 2822: Maximum length of subject is 998 characters
    subject = models.CharField(
        _("subject"), max_length=256,
        null=True, blank=True)

    sender = models.ForeignKey(
        "mailer.Sender", on_delete=models.CASCADE,
        verbose_name=_("sender"),
        null=True, blank=True)

    body_template = models.ForeignKey(
        "mailer.Template", on_delete=models.CASCADE,
        verbose_name=_("body template"),
        blank=True, null=True)
    body_str = models.TextField(
        _("body str"), null=True, blank=True)

    from_email = models.EmailField(
        _("from email"), null=True, blank=True)
    to = ArrayField(
        models.EmailField(), verbose_name=_("to"),
        null=True, blank=True)
    cc = ArrayField(
        models.EmailField(), verbose_name=_("cc"),
        null=True, blank=True)
    bcc = ArrayField(
        models.EmailField(), verbose_name=_("bcc"),
        null=True, blank=True)
    reply_to = ArrayField(
        models.EmailField(), verbose_name=_("reply to"),
        null=True, blank=True)

    alternatives = models.ManyToManyField(
        "mailer.Template",
        related_name="message_templates",
        verbose_name=_("alternatives"),
        blank=True)

    objects = MessageTemplateManager()

    def as_queue_data(self) -> dict:
        return dict(
            subject=self.subject,
            sender=self.sender,
            body_template=self.body_template,
            body_str=self.body_str,
            from_email=self.from_email,
            to=self.to,
            cc=self.cc,
            bcc=self.bcc,
            reply_to=self.reply_to,
        )

    def __str__(self) -> str:
        return f"{self.code} ({self.pk})"
