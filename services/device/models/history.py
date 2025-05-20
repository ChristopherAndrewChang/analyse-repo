from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .constants import DEVICE_ID_LENGTH

if TYPE_CHECKING:
    from device.models import Device


logger = logging.getLogger(__name__)
__all__ = (
    "DeviceHistoryQuerySet",
    "DeviceHistoryManager",
    "DeviceHistory",
)


class DeviceHistoryQuerySet(models.QuerySet):
    def revoke(self) -> int:
        return self.update(is_revoked=True, revoked_time=timezone.now())


_DeviceHistoryManagerBase = models.Manager.from_queryset(
    DeviceHistoryQuerySet
)  # type: type[DeviceHistoryQuerySet]


class DeviceHistoryManager(_DeviceHistoryManagerBase, BaseManager):
    def create_from_device(self, device: Device) -> DeviceHistory:
        instance, _ = self.model.objects.filter(
            is_revoked=False
        ).get_or_create(
            user_id=device.user_id,
            device_id=device.device_id,
            defaults={
                "platform_id": device.platform_id,
                "registered_at": device.registered_at,
            }
        )
        instance.name = device.name
        instance.device_property = device.device_property
        instance.last_login = device.last_login
        instance.save()
        return instance


class DeviceHistory(models.Model):
    user_id = models.PositiveIntegerField(
        _("user id"),
        help_text=_("User id from authn service."))
    platform_id: int
    platform = models.ForeignKey(
        "device.Platform", on_delete=models.CASCADE,
        verbose_name=_("platform"))

    name = models.CharField(
        _("name"), max_length=256)
    device_id = models.CharField(
        _("device id"), max_length=DEVICE_ID_LENGTH)
    device_property = models.JSONField(
        _("device property"), null=True, blank=True,
        help_text=_("More detail device properties."))

    registered_at = models.DateTimeField(
        _("registered at"),
        help_text=_("Registered date for the first time."))
    last_login = models.DateTimeField(
        _("last login"), null=True, blank=True,
        help_text=_("Last login date to this device."))

    is_revoked = models.BooleanField(
        _("revoked status"), default=False, db_index=True,
        help_text=_("Revoked session status."))
    revoked_time = models.DateTimeField(
        _("revoked time"), null=True, blank=True)

    objects = DeviceHistoryManager()
