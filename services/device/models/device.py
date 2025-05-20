from __future__ import annotations
from typing import TYPE_CHECKING

import re

import logging

from user_agents import parse as user_agent_parse

from django.db import models
from django.db.models.manager import BaseManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from idvalid_core.models import get_subid_model

from device.signals import device_create_history, device_post_revoke
from .constants import DEVICE_ID_LENGTH

if TYPE_CHECKING:
    from user_agents.parsers import UserAgent

    from django.db.models.base import ModelState

    from evercore_jwt_auth.models import TokenUser

    from idvalid_integration.protos.models import authn_pb2


logger = logging.getLogger(__name__)
__all__ = (
    "DeviceQuerySet",
    "DeviceManager",
    "Device",
)


def build_name_from_user_agent(value: str) -> str:
    agent = user_agent_parse(value)  # type: UserAgent
    if agent.is_pc:
        return "{device} - {browser} on {os}".format(
            device=agent.get_device(),
            browser=agent.browser.family,
            os=agent.get_os(),
        )
    else:
        device_name = None
        if match := re.search(r"DeviceName=([^;]+)", value, re.IGNORECASE):
            device_name = match.group(1)

        agent_device = agent.get_device()
        if device_name and device_name in agent_device:
            device_name = agent.get_os()

        return "{device} - {name}".format(
            device=agent_device,
            name=(device_name or agent.browser.family),
        )


class DeviceQuerySet(models.QuerySet):
    def owned(self, user: TokenUser) -> DeviceQuerySet:
        return self.filter(user_id=user.id)

    def annotate_current_session(
            self, session_id: int) -> DeviceQuerySet:
        return self.annotate(
            is_current_session=models.Case(
                models.When(session_id=session_id, then=models.Value(True)),
                default=models.Value(False),
                output_field=models.BooleanField()
            )
        )


_DeviceManagerBase = models.Manager.from_queryset(
    DeviceQuerySet
)  # type: type[DeviceQuerySet]


class DeviceManager(_DeviceManagerBase, BaseManager):
    def create_from_message(self, message: authn_pb2.UserLoggedIn) -> Device:
        current_time = timezone.now()

        user_agent = message.user_agent
        name = build_name_from_user_agent(user_agent)
        device_properties = {
            "user_agent": user_agent
        }

        instance, created = self.get_or_create(
            user_id=message.user_id,
            device_id=message.device_id,
            platform_id=message.platform_id,
            defaults={
                "name": name,
                "device_property": device_properties,
                "last_login": current_time,
                "last_login_ip": message.ip_address,
                "session_id": message.session_id,
            })  # type: Device, bool
        if not created:
            instance.name = name
            if (device_property := instance.device_property) is not None:
                device_property.update(device_properties)
            else:
                instance.device_property = device_properties
            instance.last_login = current_time
            instance.last_login_ip = message.ip_address
            instance.session_id = message.session_id
            instance.save(update_fields=[
                "name",
                "device_property",
                "last_login",
                "last_login_ip",
                "session_id",
            ])
        return instance


class Device(get_subid_model()):
    _state: ModelState

    user_id = models.PositiveIntegerField(
        _("user id"),
        help_text=_("User id from authn service."))
    platform_id: int
    platform = models.ForeignKey(
        "device.Platform", on_delete=models.CASCADE,
        related_name="devices", verbose_name=_("platform"))
    device_id = models.CharField(
        _("device id"), max_length=DEVICE_ID_LENGTH)

    name = models.CharField(
        _("name"), max_length=256)
    device_property = models.JSONField(
        _("device property"), null=True, blank=True,
        help_text=_("More detail device properties.")
    )  # type: dict | None
    session_id = models.PositiveBigIntegerField(
        _("session id"), unique=True)

    registered_at = models.DateTimeField(
        _("registered at"),
        auto_now_add=True,
        help_text=_("Registered date for the first time."))
    last_login_ip = models.GenericIPAddressField(
        _("last login ip address"),
        null=True, blank=True,
        help_text=_("Last login ip to this device."))
    last_login = models.DateTimeField(
        _("last login"), null=True, blank=True,
        help_text=_("Last login date to this device."))

    revoked_at = models.DateTimeField(
        _("revoke at"), null=True, blank=True,
        editable=False)
    revoked = models.BooleanField(
        _("revoke flag"), default=False)

    objects = DeviceManager()

    class Meta:
        unique_together = ("user_id", "platform", "device_id")

    def create_history(self) -> None:
        device_create_history.send(sender=self.__class__, instance=self)

    def revoke(self, using: str = None):
        self.revoked_at = timezone.now()
        self.revoked = True
        self.save(update_fields=["revoked_at", "revoked"], using=using)
        device_post_revoke.send(
            sender=self.__class__,
            instance=self,
            using=self._state.db)

    def build_name_from_user_agent(
            self,
            value: str = None, *,
            save: bool = False) -> str:
        if not value:
            value = (self.device_property or {}).get("user_agent", None)
        agent = user_agent_parse(str(value))  # type: UserAgent
        if agent.is_pc:
            result = "{device} - {browser} on {os}".format(
                device=agent.get_device(),
                browser=agent.browser.family,
                os=agent.get_os(),
            )
        else:
            device_name = None
            if match := re.search(r"DeviceName=([^;]+)", value, re.IGNORECASE):
                device_name = match.group(1)

            agent_device = agent.get_device()
            if device_name and device_name in agent_device:
                device_name = agent.get_os()

            result = "{device} - {name}".format(
                device=agent_device,
                name=(device_name or agent.browser.family),
            )
        self.name = result
        if save:
            self.save(update_fields=["name"])
        return result
