from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from typing import Any
    from authn.models import RefreshToken


logger = logging.getLogger(__name__)
__all__ = (
    "RefreshTokenPluginBase",
)


class RefreshTokenPluginBase(models.Model):
    objects: models.Manager

    refresh_token_id: int
    refresh_token = models.OneToOneField(
        "authn.RefreshToken", on_delete=models.CASCADE,
        primary_key=True,
        verbose_name=_("refresh token")
    )  # type: RefreshToken

    class Meta:
        abstract = True

    def get_extra_claims(self) -> dict[str, Any]:
        raise NotImplementedError
