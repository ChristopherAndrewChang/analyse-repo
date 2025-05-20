from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from evercore.utils import get_client_ip

from idvalid_integration.tasks import (
    call_task,
)

from authn.tasks import constants

if TYPE_CHECKING:
    from celery import Celery
    from rest_framework.request import Request
    from authn.models import (
        Enrollment,
        ForgetPassword,
        User,
        UserProfile,
        Platform,
        Session,
        EmailOTP,
        ChangeEmail,
    )


logger = logging.getLogger(__name__)
__all__ = (
    "call_signal_enrollment_post_create",
    "call_signal_forget_password_post_create",
    "call_signal_change_email_post_create",
    "call_signal_user_logged_in",
    "call_signal_platform_post_create",
    "call_signal_platform_post_update",
    "call_signal_platform_post_delete",
    "call_signal_session_post_create",
    "call_signal_session_post_delete",
    "call_signal_email_otp_post_challenge_create",
    "call_signal_account_post_create",
    "call_signal_user_post_active_flag_update",
    "call_signal_profile_post_update",
)


def call_signal_enrollment_post_create(
        instance: Enrollment, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_SIGNAL_ENROLLMENT_POST_CREATE,
        app=app,
        args=(instance.pk,),
        exchange=constants.EXCHANGE,
        routing_key=constants.ROUTING_SIGNAL,
        **task_opts)


def call_signal_forget_password_post_create(
        instance: ForgetPassword, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_SIGNAL_FORGET_PASSWORD_POST_CREATE,
        app=app,
        args=(instance.pk,),
        exchange=constants.EXCHANGE,
        routing_key=constants.ROUTING_SIGNAL,
        **task_opts)


def call_signal_change_email_post_create(
        instance: ChangeEmail, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_SIGNAL_CHANGE_EMAIL_POST_CREATE,
        app=app,
        args=(instance.pk,),
        exchange=constants.EXCHANGE,
        routing_key=constants.ROUTING_SIGNAL,
        **task_opts)


def call_signal_user_logged_in(
        instance: User, request: Request, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_SIGNAL_USER_LOGGED_IN,
        app=app,
        kwargs={
            "user_id": instance.pk,
            "platform_id": request.platform.pk,
            "device_id": request.COOKIES.get("device_id"),
            "user_agent": request.headers["user-agent"],
            "session_id": request.idvalid_session.id,
            "ip_address": get_client_ip(request),
        },
        kwargsrepr="login info",
        exchange=constants.EXCHANGE,
        routing_key=constants.ROUTING_SIGNAL,
        **task_opts)


def call_signal_platform_post_create(
        instance: Platform, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_SIGNAL_PLATFORM_POST_CREATE,
        app=app,
        args=(instance.pk,),
        exchange=constants.EXCHANGE,
        routing_key=constants.ROUTING_SIGNAL,
        **task_opts)


def call_signal_platform_post_update(
        instance: Platform, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_SIGNAL_PLATFORM_POST_UPDATE,
        app=app,
        args=(instance.pk,),
        exchange=constants.EXCHANGE,
        routing_key=constants.ROUTING_SIGNAL,
        **task_opts)


def call_signal_platform_post_delete(
        instance: Platform, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_SIGNAL_PLATFORM_POST_DELETE,
        app=app,
        args=(instance.pk,),
        exchange=constants.EXCHANGE,
        routing_key=constants.ROUTING_SIGNAL,
        **task_opts)


def call_signal_session_post_create(
        instance: Session, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_SIGNAL_SESSION_POST_CREATE,
        app=app,
        args=(instance.pk,),
        exchange=constants.EXCHANGE,
        routing_key=constants.ROUTING_SIGNAL,
        **task_opts)


def call_signal_session_post_delete(
        instance: Session, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_SIGNAL_SESSION_POST_DELETE,
        app=app,
        args=(instance.pk,),
        kwargs={
            "user_id": instance.user_id,
            "platform_id": instance.platform_id,
            "device_id": instance.device_id,
            "is_mobile": instance.is_mobile,
        },
        kwargsrepr="authn.Session",
        exchange=constants.EXCHANGE,
        routing_key=constants.ROUTING_SIGNAL,
        **task_opts)


def call_signal_email_otp_post_challenge_create(
        instance: EmailOTP, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_SIGNAL_EMAIL_OTP_POST_CHALLENGE_CREATE,
        app=app,
        args=(instance.pk,),
        exchange=constants.EXCHANGE,
        routing_key=constants.ROUTING_SIGNAL,
        **task_opts)


def call_signal_account_post_create(
        instance: User, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_SIGNAL_ACCOUNT_POST_CREATE,
        app=app,
        args=(instance.pk,),
        exchange=constants.EXCHANGE,
        routing_key=constants.ROUTING_SIGNAL,
        **task_opts)


def call_signal_user_post_active_flag_update(
        instance: User, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_SIGNAL_USER_POST_ACTIVE_FLAG_UPDATE,
        app=app,
        args=(instance.pk,),
        exchange=constants.EXCHANGE,
        routing_key=constants.ROUTING_SIGNAL,
        **task_opts)


def call_signal_profile_post_update(
        instance: UserProfile, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_SIGNAL_PROFILE_POST_UPDATE,
        app=app,
        args=(instance.user_id,),
        exchange=constants.EXCHANGE,
        routing_key=constants.ROUTING_SIGNAL,
        **task_opts)
