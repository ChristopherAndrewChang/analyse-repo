from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from rest_framework.generics import ListAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST

from evercore_jwt_auth.rest_framework.authentication import JWTStatelessUserAuthentication

from device.models import Device
from .permissions import DeviceRegisteredPermission

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = ("DeviceView", "DeviceRevokeView")


class DeviceView(ListAPIView):
    authentication_classes = (JWTStatelessUserAuthentication,)
    permission_classes = (
        IsAuthenticated,
        # DeviceRegisteredPermission,
    )

    def get_queryset(self):
        user = self.request.user
        return Device.objects.owned(
            user
        ).filter(
            revoked=False
        ).select_related(
            "platform"
        ).order_by(
            "-registered_at"
        ).annotate_current_session(
            user.session_id
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # request_device_id = request.device.device_id
        return Response([
            {
                "subid": obj.subid,
                "name": obj.name,
                "registered_at": obj.registered_at,
                "last_login": obj.last_login,
                "is_current_session": obj.is_current_session,
                "platform": {
                    "name": obj.platform.name,
                    "platform_type": obj.platform.platform_type,
                },
            }
            for obj in queryset
        ])


class DeviceRevokeView(DestroyAPIView):
    lookup_field = "subid"
    authentication_classes = (JWTStatelessUserAuthentication,)
    permission_classes = (
        IsAuthenticated,
        # DeviceRegisteredPermission,
    )

    def get_queryset(self):
        user = self.request.user
        return Device.objects.owned(
            self.request.user
        ).filter(
            revoked=False
        ).annotate_current_session(
            user.session_id
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()  # type: Device
        # if instance.device_id == request.device.device_id:
        #     return Response({
        #         "detail": "Unable to revoke current device, please use logout."
        #     }, status=HTTP_400_BAD_REQUEST)
        # self.perform_destroy(instance)
        instance.revoke()
        return Response(status=HTTP_204_NO_CONTENT)
