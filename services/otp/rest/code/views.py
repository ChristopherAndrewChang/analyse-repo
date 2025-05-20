from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from otp.models import Code

from .filtersets import CodeFilterSet
from .permissions import ActiveCodePermission
from .serializers import CodeSerializer

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = ("CodeView",)


class CodeView(CreateAPIView):
    serializer_class = CodeSerializer
    filter_backends = (
        DjangoFilterBackend,
    )
    filterset_class = CodeFilterSet
    queryset = Code.objects.active()
    permission_classes = (ActiveCodePermission,)
    lookup_field = 'subid'
    authentication_classes = ()

    def create(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
