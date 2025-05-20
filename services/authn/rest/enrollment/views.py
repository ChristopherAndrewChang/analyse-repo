from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from rest_framework.generics import CreateAPIView

from .serializers import EmailSerializer, PhoneSerializer

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "EmailView",
    "PhoneView",
)


class EmailView(CreateAPIView):
    serializer_class = EmailSerializer
    authentication_classes = ()
    permission_classes = ()


class PhoneView(CreateAPIView):
    serializer_class = PhoneSerializer
    authentication_classes = ()
    permission_classes = ()
