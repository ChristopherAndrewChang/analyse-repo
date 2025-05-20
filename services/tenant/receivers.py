from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import transaction
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from tenant.integration import tasks
from tenant.models import (
    Tenant,
    TenantConfig,
    TenantUser,
)

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "on_tenant_post_save",
    "on_tenant_user_post_save",
    "on_tenant_user_post_delete",
)


@receiver(post_save, sender=Tenant)
def on_tenant_post_save(
        instance: Tenant, using: str, created: bool, **kwargs):
    if created:
        # init tenant config
        TenantConfig.objects.create(tenant=instance)

    def call_task():
        tasks.call_signal_tenant_post_save(instance)
    transaction.on_commit(call_task, using=using)


@receiver(post_save, sender=TenantUser)
def on_tenant_user_post_save(
        instance: TenantUser, using: str, **kwargs):
    def call_task():
        tasks.call_signal_tenant_user_post_save(instance)
    transaction.on_commit(call_task, using=using)


@receiver(post_delete, sender=TenantUser)
def on_tenant_user_post_delete(
        instance: TenantUser, using: str, **kwargs):
    def call_task():
        tasks.call_signal_tenant_user_post_delete(instance)
    transaction.on_commit(call_task, using=using)
