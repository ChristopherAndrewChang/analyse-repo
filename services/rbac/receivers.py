from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import transaction
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from rbac.integration import tasks
from rbac.models import (
    RoleUser,
)

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "on_role_user_post_save",
    "on_role_user_post_delete",
)


@receiver(post_save, sender=RoleUser)
def on_role_user_post_save(
        instance: RoleUser, using: str, created: bool, **kwargs):
    if created:
        def call_task():
            tasks.call_signal_role_user_post_create(instance)
        transaction.on_commit(call_task, using=using)


@receiver(post_delete, sender=RoleUser)
def on_role_user_post_delete(
        instance: RoleUser, using: str, **kwargs):
    def call_task():
        tasks.call_signal_role_user_post_delete(instance)
    transaction.on_commit(call_task, using=using)
