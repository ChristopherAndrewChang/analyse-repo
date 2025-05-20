from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from celery import current_app as celery_app

from idvalid_integration.protos.models import authn_pb2

from authn.models import Session
from authn.tasks import constants

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "external_session_revoke_task",
)


@celery_app.task(
    name=constants.TASK_EXTERNAL_SESSION_REVOKE,
    queue=constants.QUEUE_EXTERNAL,
    shared=False)
def external_session_revoke_task(message: bytes):
    message = authn_pb2.Session.FromString(message)
    instance = Session.objects.get(pk=message.id)  # type: Session
    instance.delete()
