from __future__ import annotations
from typing import TYPE_CHECKING

import re

from django.core.exceptions import (
    ValidationError,
)
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    pass


__all__ = (
    "ContainsLowerCaseValidator",
    "ContainsUpperCaseValidator",
    "ContainsNumberValidator",
    "ContainsNonWordValidator",
)


class ContainsLowerCaseValidator:
    detail = _(
        "Must contains at least one lowercase character.")
    help_text = _(
        "Your password must contain at least one lowercase character.")

    def validate(self, password: str, user=None):
        if not re.search(r'[a-z]', password):
            raise ValidationError(self.detail, code="no_lower")

    def get_help_text(self):
        return self.help_text


class ContainsUpperCaseValidator:
    detail = _("Must contains at least one uppercase letter.")
    help_text = _(
        "Your password must contain at least one uppercase character.")

    def validate(self, password: str, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError(self.detail, code="no_upper")

    def get_help_text(self):
        return self.help_text


class ContainsNumberValidator:
    detail = _("Must contains at least one number.")
    help_text = _(
        "Your password must contain at least one number character.")

    def validate(self, password: str, user=None):
        if not re.search(r'\d', password):
            raise ValidationError(self.detail, code="no_number")

    def get_help_text(self):
        return self.help_text


class ContainsNonWordValidator:
    detail = _("Must contains at least one special character.")

    def validate(self, password: str, user=None):
        if not re.search(r'[\W_]', password):
            raise ValidationError(self.detail, code="no_special")
