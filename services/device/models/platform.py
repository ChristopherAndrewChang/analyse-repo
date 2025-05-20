from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.manager import BaseManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from idvalid_core.models import get_subid_model


if TYPE_CHECKING:
    from idvalid_integration.protos.models import authn_pb2


logger = logging.getLogger(__name__)
__all__ = (
    "PlatformQuerySet",
    "PlatformManager",
    "Platform",
)


class PlatformQuerySet(models.QuerySet):
    def delete(self) -> int:
        return self.update(is_deleted=True, deleted_time=timezone.now())


_PlatformManagerBase = models.Manager.from_queryset(
    PlatformQuerySet
)  # type: type[PlatformQuerySet]


class PlatformManager(_PlatformManagerBase, BaseManager):
    def create_or_update_from_message(
            self, message: authn_pb2.Platform) -> Platform:

        try:
            instance = self.model.objects.get(pk=message.id)
        except self.model.DoesNotExist:
            instance = self.model(pk=message.id)
        instance.subid = message.subid
        instance.name = message.name
        instance.platform_type = message.type
        instance.is_deleted = False
        instance.deleted_time = None
        instance.save()
        return instance


class Platform(get_subid_model()):
    # platform_id = models.PositiveIntegerField(
    #     _("platform id"), unique=True,
    #     help_text=_("Save platform id from authn service."))
    name = models.CharField(
        _("name"), max_length=150)
    platform_type = models.CharField(
        _("platform type"), max_length=32)

    is_deleted = models.BooleanField(
        _("deleted flag"),
        default=False, editable=False)
    deleted_time = models.DateTimeField(
        _("deleted time"),
        null=True, blank=True, editable=False)

    objects = PlatformManager()

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.deleted_time = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_time"])
