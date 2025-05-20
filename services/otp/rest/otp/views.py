from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import CreateAPIView, get_object_or_404
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from evercore_jwt_auth.rest_framework.authentication import JWTStatelessUserAuthentication

from otp.models import Otp

from .filtersets import ApplyOtpFilterSet
from .permissions import ApplyOtpPermission, OwnerPermission
from .serializers import ApplySerializer

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = ("OtpView",)


class OtpView(CreateAPIView):
    serializer_class = ApplySerializer
    filter_backends = (
        DjangoFilterBackend,
    )
    filterset_class = ApplyOtpFilterSet
    queryset = Otp.objects.active()
    permission_classes = (ApplyOtpPermission, OwnerPermission)
    lookup_object_id = 'object_id'
    lookup_usage = 'usage'
    authentication_classes = (
        JWTStatelessUserAuthentication,
    )

    def permission_denied(self, request, message=None, code=None):
        """
        If request is not permitted, determine what kind of exception to raise.
        """
        # if request.authenticators and not request.successful_authenticator:
        #     raise exceptions.NotAuthenticated()
        raise PermissionDenied(detail=message, code=code)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        object_id_key = self.lookup_object_id
        if object_id_key not in self.kwargs:
            raise AssertionError(
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_object_id` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, object_id_key))

        usage_key = self.lookup_usage
        if usage_key not in self.kwargs:
            raise AssertionError(
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_usage` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, usage_key))

        filter_kwargs = {
            "object_id": self.kwargs[object_id_key],
            "usage": self.kwargs[usage_key],
        }
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def create(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
