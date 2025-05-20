from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from esl_core.settings import AppSetting

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = ("mailer_settings", )


DEFAULTS = {}


MANDATORY = ()


REQUIRED = ("CDN_DOMAIN", "FE_SITE")


mailer_settings = AppSetting(
    "MAILER_SETTINGS",
    DEFAULTS,
    name="MailerSetting",
    mandatory=MANDATORY,
    required=REQUIRED,
    check_required_immediately=True)
