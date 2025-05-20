from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from idvalid_integration.tasks import call_task

from tenant.tasks import constants

if TYPE_CHECKING:
    from celery import Celery
    from tenant.models import (
        Tenant,
        TenantUser,
    )


logger = logging.getLogger(__name__)
__all__ = (
    "call_signal_tenant_post_save",
    "call_signal_tenant_user_post_save",
    "call_signal_tenant_user_post_delete",
)


def call_signal_tenant_post_save(
        instance: Tenant, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_SIGNAL_TENANT_POST_SAVE,
        app=app,
        args=(instance.pk,),
        exchange=constants.EXCHANGE,
        routing_key=constants.ROUTING_SIGNAL,
        **task_opts)


def call_signal_tenant_user_post_save(
        instance: TenantUser, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_SIGNAL_TENANT_USER_POST_SAVE,
        app=app,
        args=(instance.tenant_id, instance.user_id),
        exchange=constants.EXCHANGE,
        routing_key=constants.ROUTING_SIGNAL,
        **task_opts)


def call_signal_tenant_user_post_delete(
        instance: TenantUser, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_SIGNAL_TENANT_USER_POST_DELETE,
        app=app,
        args=(instance.tenant_id, instance.user_id),
        exchange=constants.EXCHANGE,
        routing_key=constants.ROUTING_SIGNAL,
        **task_opts)
