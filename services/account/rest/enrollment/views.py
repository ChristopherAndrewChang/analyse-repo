from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from rest_framework.generics import CreateAPIView

from .serializers import CreateSerializer

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = ("CreateView",)


class CreateView(CreateAPIView):
    serializer_class = CreateSerializer
    authentication_classes = ()
