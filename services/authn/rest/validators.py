from __future__ import annotations
from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _

from rest_framework.exceptions import ValidationError

if TYPE_CHECKING:
    pass


__all__ = (
    "DigitValidator",
)


class DigitValidator:
    message = _("Expected digits.")

    def __call__(self, value):
        if not isinstance(value, (str, bytes)):
            value = str(value)
        if not value.isdigit():
            raise ValidationError(self.message)
