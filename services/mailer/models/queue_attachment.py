from __future__ import annotations
from typing import TYPE_CHECKING

import logging
import mimetypes

from django.db import models
from django.db.models.signals import pre_save

from django.core.files import File
from django.dispatch.dispatcher import receiver
from django.utils.translation import gettext_lazy as _

from esl_core.models.fields import FileField
from mailer.file_paths import queue_attachment_file_path

if TYPE_CHECKING:
    from typing import Type


logger = logging.getLogger(__name__)
__all__ = (
    "QueueAttachmentQuerySet",
    "QueueAttachmentManager",
    "QueueAttachment",
)


class QueueAttachmentQuerySet(models.QuerySet):
    def create_from_stream(
            self, stream, filename: str = None,
            **kwargs) -> QueueAttachment:
        if filename is None:
            try:
                # get filename from stream.name
                # in case type of stream is a subclass of
                # _IOBase class that has name attribute
                filename = stream.name
            except AttributeError:
                raise ValueError("filename must be provided")
        stream.seek(0)
        return self.create(
            file=File(stream, filename),
            **kwargs)


_QueueAttachmentManagerBase = models.Manager.from_queryset(
    QueueAttachmentQuerySet
)  # type: Type[QueueAttachmentQuerySet]


class QueueAttachmentManager(_QueueAttachmentManagerBase):
    pass


class QueueAttachment(models.Model):
    queue = models.ForeignKey(
        "mailer.MessageQueue", on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name=_("queue"))
    filename = models.CharField(
        _("filename"), max_length=256)  # type: str
    file = FileField(
        _("file"), upload_to=queue_attachment_file_path,
        filename_field="filename")
    mimetype = models.CharField(
        _("mimetype"), max_length=256, blank=True)  # type: str

    objects = QueueAttachmentManager()


@receiver(pre_save, sender=QueueAttachment)
def queue_attachment_pre_save(instance: QueueAttachment, **kwargs):
    if not instance.mimetype and (name := instance.filename):
        instance.mimetype = mimetypes.guess_type(name)[0]
