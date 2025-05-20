from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from idvalid_integration.tasks import (
    authn as auth_tasks,
)
from idvalid_integration.protos.models import authn_pb2

if TYPE_CHECKING:
    from celery import Celery
    from device.models import Device


logger = logging.getLogger(__name__)
__all__ = (
    "call_external_auth_session_revoke",
)


def call_external_auth_session_revoke(
        instance: Device, *,
        app: Celery = None,
        **task_opts):
    message = authn_pb2.Session(
        id=instance.session_id,
        user_id=instance.user_id,
        platform_id=instance.platform_id,
        device_id=instance.device_id,)
    return auth_tasks.session_revoke(message, app=app, **task_opts)
