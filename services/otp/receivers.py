from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from otp import signals
from otp.integration import tasks
from otp.models import Otp

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    # "on_code_post_save",
    "on_otp_post_save",
    "on_otp_applied",
)


# @receiver(post_save, sender=Code)
# def on_code_post_save(instance: Code, created: bool, **kwargs):
#     if created:
#         tasks.call_code_post_create(instance)


@receiver(post_save, sender=Otp)
def on_otp_post_save(instance: Otp, created: bool, using: str, **kwargs):
    if created:
        def call_task():
            tasks.call_signal_otp_post_create(instance)
        transaction.on_commit(call_task, using=using)


@receiver(signals.otp_applied, sender=Otp)
def on_otp_applied(instance: Otp, using: str, **kwargs):
    def call_task():
        tasks.call_signal_otp_apply(instance)
    transaction.on_commit(call_task, using=using)
