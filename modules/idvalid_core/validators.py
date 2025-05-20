from __future__ import annotations
from typing import TYPE_CHECKING

from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    pass


__all__ = ("UnicodeUsernameValidator",)


@deconstructible
class UnicodeUsernameValidator(validators.RegexValidator):
    regex = r"^[\w.]+\Z"
    message = _(
        "Enter a valid username. This value may contain only letters, "
        "numbers, and ./_ characters."
    )
    flags = 0
