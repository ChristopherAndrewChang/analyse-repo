from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models

from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from typing import Type


logger = logging.getLogger(__name__)
__all__ = ("DeveloperEmail", )


class DeveloperEmail(models.Model):
    email = models.EmailField(
        _("email"), unique=True)  # type: str
    is_active = models.BooleanField(
        _("active flag"), default=True)

    created = models.DateTimeField(
        _("created time"), auto_now_add=True, editable=False)
    modified = models.DateTimeField(
        _("created time"), auto_now=True, editable=False)

    def __str__(self) -> str:
        return f"{self.email}"
