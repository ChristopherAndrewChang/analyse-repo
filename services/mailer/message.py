from __future__ import annotations
from typing import TYPE_CHECKING

from django.core.mail import get_connection
from django.core.mail.message import (
    EmailMessage as dj_EmailMessage,
    EmailMultiAlternatives as dj_EmailMultiAlternatives)

if TYPE_CHECKING:
    pass


__all__ = ("EmailMessage", "EmailMultiAlternatives")


# noinspection PyUnresolvedReferences,PyAttributeOutsideInit
class _EmailMessageMixin:
    def get_connection(self, fail_silently=False, **connection_config):
        if not self.connection:
            self.connection = get_connection(
                fail_silently=fail_silently, **connection_config)
        return self.connection

    def send(self, fail_silently=False, **kwargs) -> int:
        """Send the email message."""
        if not self.recipients():
            # Don't bother creating the network connection if there's nobody to
            # send to.
            return 0
        return self.get_connection(fail_silently, **kwargs).send_messages([self])


class EmailMessage(_EmailMessageMixin, dj_EmailMessage):
    pass


class EmailMultiAlternatives(
        _EmailMessageMixin, dj_EmailMultiAlternatives):
    pass
