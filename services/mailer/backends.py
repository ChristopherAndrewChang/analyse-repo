"""SMTP email backend class."""
from __future__ import annotations
from typing import TYPE_CHECKING

import smtplib
import ssl
import threading

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import sanitize_address
from django.core.mail.utils import DNS_NAME

from mailer.models import DeveloperEmail

if TYPE_CHECKING:
    from typing import Sequence, Tuple
    from mailer.models import Sender


class DefaultSender:
    def __init__(self):
        self.host = settings.EMAIL_HOST
        self.port = settings.EMAIL_PORT
        self.username = settings.EMAIL_HOST_USER
        self.password = settings.EMAIL_HOST_PASSWORD
        self.tls = settings.EMAIL_USE_TLS
        self.ssl = settings.EMAIL_USE_SSL
        self.timeout = settings.EMAIL_TIMEOUT
        self.ssl_keyfile = settings.EMAIL_SSL_KEYFILE
        self.ssl_certfile = settings.EMAIL_SSL_CERTFILE
        if self.ssl and self.tls:
            raise ValueError(
                "EMAIL_USE_TLS/EMAIL_USE_SSL are mutually exclusive, so only set "
                "one of those settings to True.")


class EmailBackend(BaseEmailBackend):
    _dev_emails: Sequence[DeveloperEmail]

    def __init__(self, fail_silently: bool = False, sender: Sender = None,
                 **kwargs):
        super().__init__(fail_silently=fail_silently)
        if sender is None:
            self.sender = DefaultSender()
        else:
            self.sender = sender
        self.connection = None
        self._lock = threading.RLock()

    @property
    def connection_class(self):
        return smtplib.SMTP_SSL if self.sender.ssl else smtplib.SMTP

    @property
    def dev_emails(self) -> Tuple[str]:
        try:
            emails = self._dev_emails
        except AttributeError:
            emails = tuple(DeveloperEmail.objects.filter(
                is_active=True))
            self._dev_emails = emails
        return tuple(instance.email for instance in emails)

    def open(self):
        """
        Ensure an open connection to the email server. Return whether or not a
        new connection was required (True or False) or None if an exception
        passed silently.
        """
        if self.connection:
            # Nothing to do if the connection is already open.
            return False

        # If local_hostname is not specified, socket.getfqdn() gets used.
        # For performance, we use the cached FQDN for local_hostname.
        connection_params = {'local_hostname': DNS_NAME.get_fqdn()}
        if (timeout := self.sender.timeout) is not None:
            connection_params['timeout'] = timeout
        if self.sender.ssl:
            connection_params.update({
                'keyfile': self.sender.ssl_keyfile,
                'certfile': self.sender.ssl_certfile,
            })
        try:
            self.connection = self.connection_class(
                self.sender.host, self.sender.port, **connection_params)

            # TLS/SSL are mutually exclusive, so only attempt TLS over
            # non-secure connections.
            if not self.sender.ssl and self.sender.tls:
                self.connection.starttls(
                    keyfile=self.sender.ssl_keyfile,
                    certfile=self.sender.ssl_certfile)
            if self.sender.username and self.sender.password:
                self.connection.login(self.sender.username, self.sender.password)
            return True
        except OSError:
            if not self.fail_silently:
                raise

    def close(self):
        """Close the connection to the email server."""
        if self.connection is None:
            return
        try:
            try:
                self.connection.quit()
            except (ssl.SSLError, smtplib.SMTPServerDisconnected):
                # This happens when calling quit() on a TLS connection
                # sometimes, or when the connection was already disconnected
                # by the server.
                self.connection.close()
            except smtplib.SMTPException:
                if self.fail_silently:
                    return
                raise
        finally:
            self.connection = None

    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects and return the number of email
        messages sent.
        """
        if not email_messages:
            return 0
        with self._lock:
            new_conn_created = self.open()
            if not self.connection or new_conn_created is None:
                # We failed silently on open().
                # Trying to send would be pointless.
                return 0
            num_sent = 0
            for message in email_messages:
                sent = self._send(message)
                if sent:
                    num_sent += 1
            if new_conn_created:
                self.close()
        return num_sent

    def _send(self, email_message):
        """A helper method that does the actual sending."""
        if settings.DEBUG:
            recipients = self.dev_emails
        else:
            recipients = email_message.recipients()
        if not recipients:
            return False
        encoding = email_message.encoding or settings.DEFAULT_CHARSET
        from_email = sanitize_address(email_message.from_email, encoding)
        recipients = [sanitize_address(addr, encoding) for addr in recipients]
        message = email_message.message()
        try:
            self.connection.sendmail(from_email, recipients, message.as_bytes(linesep='\r\n'))
        except smtplib.SMTPException:
            if not self.fail_silently:
                raise
            return False
        return True
