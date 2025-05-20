from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import gettext_lazy as _

from idvalid_core.models import get_subid_model

from . import constants

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "ProfileQuerySet",
    "ProfileManager",
    "Profile",
)


class ProfileQuerySet(models.QuerySet):
    pass


_ProfileManagerBase = models.Manager.from_queryset(
    ProfileQuerySet
)  # type: type[ProfileQuerySet]


class ProfileManager(_ProfileManagerBase, BaseManager):
    pass


class Profile(get_subid_model()):
    account_id = models.CharField(
        _("account id"), unique=True,
        max_length=constants.ACCOUNT_ID_LENGTH)
    name = models.CharField(
        _("name"), max_length=256)
