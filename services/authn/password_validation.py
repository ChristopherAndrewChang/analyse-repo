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

    def validate(self, password: str | bytes, user=None):
        pattern = (
            br'[a-z]'
            if isinstance(password, bytes) else
            r'[a-z]'
        )
        if not re.search(pattern, password):
            raise ValidationError(self.detail, code="no_lower")

    def get_help_text(self):
        return self.help_text


class ContainsUpperCaseValidator:
    detail = _("Must contains at least one uppercase letter.")
    help_text = _(
        "Your password must contain at least one uppercase character.")

    def validate(self, password: str | bytes, user=None):
        pattern = (
            br'[A-Z]'
            if isinstance(password, bytes) else
            r'[A-Z]'
        )
        if not re.search(pattern, password):
            raise ValidationError(self.detail, code="no_upper")

    def get_help_text(self):
        return self.help_text


class ContainsNumberValidator:
    detail = _("Must contains at least one number.")
    help_text = _(
        "Your password must contain at least one number character.")

    def validate(self, password: str | bytes, user=None):
        pattern = (
            br'\d'
            if isinstance(password, bytes) else
            r'\d'
        )
        if not re.search(pattern, password):
            raise ValidationError(self.detail, code="no_number")

    def get_help_text(self):
        return self.help_text


class ContainsNonWordValidator:
    detail = _("Must contains at least one special character.")

    def validate(self, password: str | bytes, user=None):
        pattern = (
            br'[\W_]'
            if isinstance(password, bytes) else
            r'[\W_]'
        )
        if not re.search(pattern, password):
            raise ValidationError(self.detail, code="no_special")
