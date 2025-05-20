from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.core.mail import get_connection
from django.db import models

from django.utils.translation import gettext_lazy as _

from esl_core.models import SubIDModel

from mailer.file_paths import cert_file_path, key_file_path

if TYPE_CHECKING:
    from typing import Type, Sequence
    from mailer.backends import EmailBackend
    from .message_queue import MessageQueue


logger = logging.getLogger(__name__)
__all__ = ("Sender", )


class Sender(SubIDModel):
    code = models.CharField(
        _("code"), max_length=64, unique=True)
    host = models.CharField(
        _("host"), max_length=256, default="localhost")
    port = models.PositiveIntegerField(
        _("port"), default=25)
    username = models.EmailField(
        _("username"))
    password = models.CharField(
        _("password"), max_length=512, null=True, blank=True)
    tls = models.BooleanField(
        _("use tls?"), default=False)
    ssl = models.BooleanField(
        _("use ssl?"), default=False)
    cert_file = models.FileField(
        _("cert file"), upload_to=cert_file_path,
        null=True, blank=True)
    key_file = models.FileField(
        _("key file"), upload_to=key_file_path,
        null=True, blank=True)
    timeout = models.PositiveIntegerField(
        _("timeout"), null=True, blank=True)

    created = models.DateTimeField(
        _("created time"), auto_now_add=True, editable=False)
    modified = models.DateTimeField(
        _("created time"), auto_now=True, editable=False)

    def __str__(self) -> str:
        return f"{self.username} ({self.code})"

    @property
    def ssl_certfile(self) -> str | None:
        return self.cert_file.name

    @property
    def ssl_keyfile(self) -> str | None:
        return self.key_file.name

    def get_connection(self, *, fail_silently: bool = False) -> EmailBackend:
        return get_connection(
            "mailer.backends.EmailBackend",
            fail_silently=fail_silently,
            sender=self
        )

    def send_messages(
            self, messages: Sequence[MessageQueue], *,
            fail_silently: bool = False) -> int:
        connection = self.get_connection(fail_silently=fail_silently)
        messages = [
            message.build_message()
            for message in messages
        ]
        if not messages:
            return 0
        return connection.send_messages(messages)
