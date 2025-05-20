from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver

from enrollment.integration import tasks
from enrollment.models import Code
from enrollment.signals import code_applied

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    'on_code_post_save',
    'on_code_applied',
)


@receiver(post_save, sender=Code)
def on_code_post_save(instance: Code, created: bool, using: str, **kwargs):
    if created:
        def call_task():
            tasks.call_signal_code_post_create(instance)
        transaction.on_commit(call_task, using=using)


@receiver(code_applied, sender=Code)
def on_code_applied(instance: Code, using: str, **kwargs):
    def call_task():
        pass
    transaction.on_commit(call_task, using=using)
