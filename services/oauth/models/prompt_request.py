from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from idvalid_core.models import get_subid_model

from oauth.signals import post_answer

if TYPE_CHECKING:
    from django.db.models.base import ModelState
    from .application import Application


logger = logging.getLogger(__name__)
__all__ = (
    "PromptQuerySet",
    "PromptRequestManager",
    "PromptRequest",
)


class PromptQuerySet(models.QuerySet):
    pass


_PromptRequestManagerBase = models.Manager.from_queryset(
    PromptQuerySet
)  # type: type[PromptQuerySet]


class PromptRequestManager(_PromptRequestManagerBase, BaseManager):
    pass


class PromptRequest(get_subid_model()):
    _state: ModelState

    ANSWER_ACCEPTED = "accepted"
    ANSWER_REJECTED = "rejected"
    ANSWER_CHOICES = (
        (ANSWER_ACCEPTED, "Accepted"),
        (ANSWER_REJECTED, "Rejected"),
    )

    application_id: int
    application = models.ForeignKey(
        "oauth.Application", on_delete=models.CASCADE
    )  # type: Application
    user_id = models.PositiveBigIntegerField(_("user id"))

    expires = models.DateTimeField(
        _("expires"), null=True, blank=True)

    answer = models.TextField(
        _("answer"),
        max_length=32, choices=ANSWER_CHOICES,
        null=True, blank=True)
    answer_time = models.DateTimeField(
        _("answer time"), null=True, blank=True)

    created_time = models.DateTimeField(
        _("created time"), auto_now_add=True)

    objects = PromptRequestManager()

    def is_alive(self) -> bool:
        return self.expires >= timezone.now()

    def set_answer(self, answer: str, *, save: bool = True):
        self.answer = answer
        self.answer_time = timezone.now()
        if save:
            self.save(update_fields=["answer", "answer_time"])
            post_answer.send(sender=self.__class__, instance=self)

    def notify_callback(self):
        if not self.answer:
            raise TypeError("has no answer")
        self.application.call_prompt_callback(
            {
                "type": "prompt",
                "id": self.subid,
                "answer": self.answer
            }
        )
