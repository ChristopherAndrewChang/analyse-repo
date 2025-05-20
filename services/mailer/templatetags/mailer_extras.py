from __future__ import annotations
from typing import TYPE_CHECKING

from django import template

from mailer.settings import mailer_settings

if TYPE_CHECKING:
    pass


register = template.Library()


@register.simple_tag(takes_context=True)
def mailer_cdn_domain(context):
    return context.get("cdn_domain", None) or mailer_settings.CDN_DOMAIN.rstrip("/")


@register.simple_tag(takes_context=True)
def mailer_origin(context):
    return context.get("origin", None) or mailer_settings.FE_SITE.rstrip("/")
