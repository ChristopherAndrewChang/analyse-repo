from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.contrib.auth.hashers import make_password, check_password

from django.db import models
from django.db.models.manager import BaseManager
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from idvalid_core.models import get_subid_model

from otp.generators import otp_number
from otp.integration.rpc import sign_code

from . import constants

if TYPE_CHECKING:
    from typing import Self
    from .recipient import Recipient
    from .usage import Usage
    from .issuer import Issuer


logger = logging.getLogger(__name__)
__all__ = (
    "CodeQuerySet",
    "CodeManager",
    "Code",
)


class CodeQuerySet(models.QuerySet):
    def ready(self, *args, **kwargs) -> Self:
        return self.filter(
            *args, code__isnull=False, **kwargs)

    def active(self, *args, **kwargs) -> Self:
        return self.filter(
            *args, suppressed=False,
            confirmed=False, applied=False, **kwargs)

    def confirmation(self, *args, **kwargs) -> Self:
        return self.filter(
            *args, confirmed=False, applied=True)


_CodeManagerBase = models.Manager.from_queryset(
    CodeQuerySet
)  # type: type[CodeQuerySet]


class CodeManager(_CodeManagerBase, BaseManager):
    pass


class Code(get_subid_model()):
    CODE_LENGTH = 128
    REF_ID_LENGTH = 64
    DEVICE_ID_LENGTH = 64

    code = models.CharField(
        _("code"), max_length=constants.CODE_LENGTH,
        null=True, editable=False)
    expires = models.DateTimeField(
        _("expires"))
    recipient = models.ForeignKey(
        "otp.Recipient", on_delete=models.CASCADE,
        verbose_name=_("recipient"))  # type: Recipient
    usage = models.ForeignKey(
        "otp.Usage", on_delete=models.CASCADE,
        verbose_name=_("usage"))  # type: Usage
    issuer = models.ForeignKey(
        "otp.Issuer", on_delete=models.CASCADE,
        verbose_name=_("issuer"))  # type: Issuer
    ref_id = models.CharField(
        _("ref id"), max_length=constants.REF_ID_LENGTH)
    device_id = models.CharField(
        _("device id"), max_length=constants.DEVICE_ID_LENGTH,
        null=True, blank=True)

    key = models.BinaryField(
        _("private key"))

    suppressed = models.BooleanField(
        _("suppressed"), default=False)
    confirmed = models.BooleanField(
        _("confirmed"), default=False)
    applied = models.BooleanField(
        _("applied"), default=False)

    created = models.DateTimeField(
        _("created"), auto_now_add=True)

    objects = CodeManager()

    @cached_property
    def signature(self) -> bytes:
        if not self.applied:
            raise TypeError(
                "signature is unavailable for non applied code")
        return sign_code(self).signature

    def is_expired(self) -> bool:
        return timezone.now() > self.expires

    def is_ready(self) -> bool:
        return self.code is not None

    def set_code(self, raw_code: str):
        self.code = make_password(raw_code)
        self._code = raw_code

    def prepare_code(self, *, save: bool = True) -> str:
        if self.is_ready():
            raise TypeError("already prepared")

        code = otp_number()
        self.set_code(code)
        if save:
            self.save(update_fields=["code"])
        return code

    def check_code(self, raw_code: str) -> bool:
        if not self.is_ready():
            return False

        def upgrade(value: str):
            self.set_code(value)
            self._code = None
            self.save(update_fields=["code"])

        return check_password(raw_code, self.code, upgrade)

    def allow_suppression(self):
        return not (self.suppressed or self.confirmed)

    def suppress(self, *, save: bool = True):
        if self.suppressed:
            raise TypeError("already suppressed")
        if self.confirmed:
            raise TypeError("unable to suppress due to user confirmed")
        self.suppressed = True
        if save:
            self.save(update_fields=["suppressed"])

    def apply(self, *, save: bool = True):
        if self.applied:
            raise TypeError("already applier")
        self.applied = True
        if save:
            self.save(update_fields=["applied"])

    def confirm(
            self, *, save: bool = True):
        if self.confirmed:
            raise TypeError("already confirmed")
        if not self.applied:
            raise TypeError("code is not applied")
        self.confirmed = True
        if save:
            self.save(update_fields=["confirmed"])
