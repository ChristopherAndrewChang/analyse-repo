from __future__ import annotations
from typing import TYPE_CHECKING

import logging
import mimetypes

from django.db import models
from django.db.models.signals import pre_save

from django.dispatch.dispatcher import receiver
from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _

from .constants import DEFAULT_TEMPLATE_MIME_TYPE

if TYPE_CHECKING:
    from typing import Tuple
    from django.template.backends.django import (
        Template as dj_Template)


logger = logging.getLogger(__name__)
__all__ = ("Template", )


class Template(models.Model):
    code = models.CharField(
        _("code"), max_length=64, unique=True)
    is_active = models.BooleanField(
        _("active flag"), default=True)

    template_path = models.CharField(
        _("template path"), max_length=512)  # type: str
    mimetype = models.CharField(
        _("mimetype"), max_length=256, blank=True)  # type: str

    def __str__(self) -> str:
        return f"{self.code} ({self.pk})"

    def render(self, context: dict) -> str:
        template = get_template(self.template_path)  # type: dj_Template
        return template.render(context)


@receiver(pre_save, sender=Template)
def template_pre_save(instance: Template, **kwargs):
    if not instance.mimetype:
        mt = mimetypes.guess_type(instance.template_path)[0]
        if not mt:
            mt = DEFAULT_TEMPLATE_MIME_TYPE
        instance.mimetype = mt
