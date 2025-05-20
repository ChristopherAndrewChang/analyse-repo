from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django_filters import rest_framework as filters

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = ("CodeFilterSet",)


class CodeFilterSet(filters.FilterSet):
    ref_id = filters.CharFilter(required=True)
