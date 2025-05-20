from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from account.integration import tasks
from account.models import Enrollment

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "on_enrollment_post_save",
)


@receiver(post_save, sender=Enrollment)
def on_enrollment_post_save(instance: Enrollment, created: bool, using: str, **kwargs):
    if created:
        def call_task():
            tasks.call_signal_enrollment_post_create(instance)
        transaction.on_commit(call_task, using=using)
