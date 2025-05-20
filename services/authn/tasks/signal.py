from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.core.mail import send_mail

from celery import current_app as celery_app

from authn.models import (
    Enrollment,
    ForgetPassword,
    Platform,
    EmailOTP,
    ChangeEmail,
    Session,
    User,
    UserMFA,
    UserProfile,
)
from authn.tasks import constants
from authn.integration import tasks

if TYPE_CHECKING:
    from celery import Task


logger = logging.getLogger(__name__)
__all__ = (
    "signal_enrollment_post_create_task",
    "signal_forget_password_post_create_task",
    "signal_change_email_post_create_task",
    "signal_user_logged_in_task",

    "signal_platform_post_create_task",
    "signal_platform_post_update_task",
    "signal_platform_post_delete_task",

    "signal_session_post_create_task",
    "signal_session_post_delete_task",

    "signal_email_otp_post_challenge_create_task",

    "signal_account_post_create_task",
    "signal_user_post_active_flag_update_task",
    "signal_profile_post_update_task",
)


@celery_app.task(
    name=constants.TASK_SIGNAL_ENROLLMENT_POST_CREATE,
    queue=constants.QUEUE_SIGNAL,
    shared=False,
    bind=True)
def signal_enrollment_post_create_task(self: Task, pk: int):
    instance = Enrollment.objects.select_related(
        "email").get(pk=pk)  # type: Enrollment
    if instance.email_id:
        params = {"email_id": instance.email_id}
    elif instance.phone_id:
        params = {"phone_id": instance.phone_id}
    else:
        raise ValueError("no email or phone")
    Enrollment.objects.exclude(
        pk=pk
    ).suppress(**params)
    tasks.call_external_enrollment_otp_create(instance, app=self._app)


@celery_app.task(
    name=constants.TASK_SIGNAL_FORGET_PASSWORD_POST_CREATE,
    queue=constants.QUEUE_SIGNAL,
    shared=False,
    bind=True)
def signal_forget_password_post_create_task(self: Task, pk: int):
    instance = ForgetPassword.objects.select_related(
        "user").get(pk=pk)  # type: ForgetPassword
    ForgetPassword.objects.exclude(
        pk=pk
    ).suppress(instance.user)
    tasks.call_external_forget_password_otp_create(
        instance, app=self._app)


@celery_app.task(
    name=constants.TASK_SIGNAL_CHANGE_EMAIL_POST_CREATE,
    queue=constants.QUEUE_SIGNAL,
    shared=False,
    bind=True)
def signal_change_email_post_create_task(self: Task, pk: int):
    instance = ChangeEmail.objects.select_related(
        "user").get(pk=pk)
    ChangeEmail.objects.exclude(
        pk=pk
    ).suppress(instance.user)
    tasks.call_external_change_email_otp_create(
        instance, app=self._app)


@celery_app.task(
    name=constants.TASK_SIGNAL_USER_LOGGED_IN,
    queue=constants.QUEUE_SIGNAL,
    shared=False,
    bind=True)
def signal_user_logged_in_task(
        self: Task, user_id: int, platform_id: int,
        device_id: str, user_agent: str, session_id: int,
        ip_address: str | None):
    tasks.call_publish_user_logged_in(
        user_id, platform_id, device_id,
        user_agent, session_id, ip_address,
        app=self._app)


@celery_app.task(
    name=constants.TASK_SIGNAL_PLATFORM_POST_CREATE,
    queue=constants.QUEUE_SIGNAL,
    shared=False,
    bind=True)
def signal_platform_post_create_task(
        self: Task, platform_id: int):
    instance = Platform.objects.get(pk=platform_id)
    tasks.call_publish_platform_create(instance, app=self._app)


@celery_app.task(
    name=constants.TASK_SIGNAL_PLATFORM_POST_UPDATE,
    queue=constants.QUEUE_SIGNAL,
    shared=False,
    bind=True)
def signal_platform_post_update_task(
        self: Task, platform_id: int):
    instance = Platform.objects.get(pk=platform_id)
    tasks.call_publish_platform_update(instance, app=self._app)


@celery_app.task(
    name=constants.TASK_SIGNAL_PLATFORM_POST_DELETE,
    queue=constants.QUEUE_SIGNAL,
    shared=False,
    bind=True)
def signal_platform_post_delete_task(
        self: Task, platform_id: int):
    tasks.call_publish_platform_delete(platform_id, app=self._app)


@celery_app.task(
    name=constants.TASK_SIGNAL_SESSION_POST_CREATE,
    queue=constants.QUEUE_SIGNAL,
    shared=False,
    bind=True)
def signal_session_post_create_task(
        self: Task, session_id: int):
    instance = Session.objects.get(pk=session_id)  # type: Session
    if instance.is_mobile:
        instance.user.mfa.inc_mobile_logged_in()
    tasks.call_publish_session_create(instance, app=self._app)


@celery_app.task(
    name=constants.TASK_SIGNAL_SESSION_POST_DELETE,
    queue=constants.QUEUE_SIGNAL,
    shared=False,
    bind=True)
def signal_session_post_delete_task(
        self: Task, session_id: int, user_id: int, platform_id: int,
        device_id: str, is_mobile: bool):
    if is_mobile:
        mfa = UserMFA.objects.get(user_id=user_id)  # type: UserMFA
        mfa.dec_mobile_logged_in()
    tasks.call_publish_session_delete(session_id, app=self._app)


@celery_app.task(
    name=constants.TASK_SIGNAL_EMAIL_OTP_POST_CHALLENGE_CREATE,
    queue=constants.QUEUE_SIGNAL,
    shared=False,
    bind=True)
def signal_email_otp_post_challenge_create_task(
        self: Task, email_otp_id: int):
    instance = EmailOTP.objects.get(pk=email_otp_id)  # type: EmailOTP
    pin = instance.generate_pin()
    send_mail(
        subject="IDValid PIN",
        message=f"Your 2fa pin: {pin}",
        from_email=None,
        recipient_list=[instance.email or instance.user.email])


@celery_app.task(
    name=constants.TASK_SIGNAL_ACCOUNT_POST_CREATE,
    queue=constants.QUEUE_SIGNAL,
    shared=False,
    bind=True)
def signal_account_post_create_task(
        self: Task, user_id: int):
    user = User.objects.get(pk=user_id)
    tasks.call_publish_account_create(user, app=self._app)


@celery_app.task(
    name=constants.TASK_SIGNAL_USER_POST_ACTIVE_FLAG_UPDATE,
    queue=constants.QUEUE_SIGNAL,
    shared=False,
    bind=True)
def signal_user_post_active_flag_update_task(
        self: Task, user_id: int):
    user = User.objects.get(pk=user_id)
    tasks.call_publish_user_active_flag(user, app=self._app)


@celery_app.task(
    name=constants.TASK_SIGNAL_PROFILE_POST_UPDATE,
    queue=constants.QUEUE_SIGNAL,
    shared=False,
    bind=True)
def signal_profile_post_update_task(
        self: Task, user_id: int):
    profile = UserProfile.objects.get(user_id=user_id)
    tasks.call_publish_profile_update(profile, app=self._app)
