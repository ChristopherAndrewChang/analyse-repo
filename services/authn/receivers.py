from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.contrib.auth.signals import (
    user_logged_in as admin_user_logged_in,
)
from django.db import transaction
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from authn.integration import tasks
from authn.models import (
    Enrollment,
    ForgetPassword,
    User,
    UserProfile,
    Platform,
    Session,
    EmailOTP,
    ChangeEmail,
    Passkey,
)
from authn.signals import (
    user_logged_in,
    # session_revoke,
    email_otp_post_challenge_create,
    account_post_create,
    user_post_active_flag_update,
)

if TYPE_CHECKING:
    from rest_framework.request import Request


logger = logging.getLogger(__name__)
__all__ = (
    "on_admin_user_logged_in",

    "on_enrollment_post_save",
    "on_forget_password_post_save",
    "on_change_email_post_save",
    "on_user_logged_in",

    "on_platform_post_save",
    "on_platform_post_delete",

    "on_session_post_save",
    "on_session_post_delete",

    "on_email_otp_post_challenge_create",

    "on_passkey_post_save",
    "on_passkey_post_delete",

    "on_account_post_create",
    "on_user_post_active_flag_update",
    "on_profile_post_save",
)


@receiver(admin_user_logged_in, sender=User)
def on_admin_user_logged_in(user: User, **kwargs):
    log = user.log
    log.admin_last_login = timezone.now()
    log.save(update_fields=["admin_last_login"])


@receiver(post_save, sender=Enrollment)
def on_enrollment_post_save(instance: Enrollment, created: bool, using: str, **kwargs):
    if created:
        def call_task():
            tasks.call_signal_enrollment_post_create(instance)
        transaction.on_commit(call_task, using=using)


@receiver(post_save, sender=ForgetPassword)
def on_forget_password_post_save(instance: ForgetPassword, created: bool, using: str, **kwargs):
    if created:
        def call_task():
            tasks.call_signal_forget_password_post_create(instance)
        transaction.on_commit(call_task, using=using)


@receiver(post_save, sender=ChangeEmail)
def on_change_email_post_save(instance: ChangeEmail, created: bool, using: str, **kwargs):
    if created:
        def call_task():
            tasks.call_signal_change_email_post_create(instance)
        transaction.on_commit(call_task, using=using)


@receiver(user_logged_in, sender=User)
def on_user_logged_in(request: Request, user: User, **kwargs):
    tasks.call_signal_user_logged_in(user, request)


@receiver(post_save, sender=Platform)
def on_platform_post_save(
        instance: Platform, created: bool, using: str, **kwargs):
    if created:
        def call_task():
            tasks.call_signal_platform_post_create(instance)

    elif instance.is_deleted:
        def call_task():
            tasks.call_signal_platform_post_delete(instance)

    else:
        def call_task():
            tasks.call_signal_platform_post_update(instance)

    transaction.on_commit(call_task, using=using)


@receiver(post_delete, sender=Platform)
def on_platform_post_delete(
        instance: Platform, using: str, **kwargs):
    def call_task():
        tasks.call_signal_platform_post_delete(instance)
    transaction.on_commit(call_task, using=using)


@receiver(post_save, sender=Session)
def on_session_post_save(
        instance: Session, created: bool, using: str, **kwargs):
    if created:
        def call_task():
            tasks.call_signal_session_post_create(instance)
        transaction.on_commit(call_task, using=using)


@receiver(post_delete, sender=Session)
def on_session_post_delete(instance: Session, using: str, **kwargs):
    def call_task():
        tasks.call_signal_session_post_delete(instance)
    transaction.on_commit(call_task, using=using)


@receiver(email_otp_post_challenge_create, sender=EmailOTP)
def on_email_otp_post_challenge_create(instance: EmailOTP, **kwargs):
    def call_task():
        tasks.call_signal_email_otp_post_challenge_create(instance)
    transaction.on_commit(call_task)


@receiver(post_save, sender=Passkey)
def on_passkey_post_save(instance: Passkey, created: bool, **kwargs):
    if created:
        instance.user.mfa.inc_passkey_device()


@receiver(post_delete, sender=Passkey)
def on_passkey_post_delete(instance: Passkey, **kwargs):
    instance.user.mfa.dec_passkey_device()


@receiver(account_post_create, sender=User)
def on_account_post_create(user: User, **kwargs):
    def call_task():
        tasks.call_signal_account_post_create(user)
    transaction.on_commit(call_task)


@receiver(user_post_active_flag_update, sender=User)
def on_user_post_active_flag_update(instance: User, **kwargs):
    def call_task():
        tasks.call_signal_user_post_active_flag_update(instance)
    transaction.on_commit(call_task)


@receiver(post_save, sender=UserProfile)
def on_profile_post_save(instance: UserProfile, created: bool, **kwargs):
    if not created:
        def call_task():
            tasks.call_signal_profile_post_update(instance)
        transaction.on_commit(call_task)
