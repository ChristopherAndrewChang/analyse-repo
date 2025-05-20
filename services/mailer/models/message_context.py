from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models

from django.utils.translation import gettext_lazy as _

from esl_core.serialization import pack_data, unpack_data

if TYPE_CHECKING:
    from typing import Type, Any


logger = logging.getLogger(__name__)
__all__ = (
    "MessageContextQuerySet",
    "MessageContextManager",
    "MessageContext",
)


class MessageContextQuerySet(models.QuerySet):
    def create(self, context: Any, **kwargs) -> MessageContext:
        return super(MessageContextQuerySet, self).create(
            context=pack_data(context))


_MessageContextManagerBase = models.Manager.from_queryset(
    MessageContextQuerySet
)  # type: Type[MessageContextQuerySet]


class MessageContextManager(_MessageContextManagerBase):
    pass


class MessageContext(models.Model):
    context = models.BinaryField(
        _("context"))
    created = models.DateTimeField(
        _("created time"), auto_now_add=True)

    objects = MessageContextManager()

    def unpack(self) -> dict:
        return unpack_data(self.context)
