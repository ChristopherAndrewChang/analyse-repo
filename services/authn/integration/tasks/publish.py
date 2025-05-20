from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from idvalid_integration.tasks import (
    authn as authn_tasks,
)
from idvalid_integration.protos.models import (
    authn_pb2,
)

from authn.models import Platform, Session, User, UserProfile

if TYPE_CHECKING:
    from celery import Celery


logger = logging.getLogger(__name__)
__all__ = (
    "call_publish_user_logged_in",

    "call_publish_platform_create",
    "call_publish_platform_update",
    "call_publish_platform_delete",

    "call_publish_session_create",
    "call_publish_session_delete",

    "call_publish_account_create",
    "call_publish_user_active_flag",
    "call_publish_profile_update",
)


def call_publish_user_logged_in(
        user_id: int, platform_id: int, device_id: str,
        user_agent: str, session_id: int, ip_address: str | None, *,
        app: Celery = None,
        **task_opts):
    message = authn_pb2.UserLoggedIn(
        user_id=user_id,
        platform_id=platform_id,
        device_id=device_id,
        user_agent=user_agent,
        session_id=session_id,
        ip_address=ip_address)
    return authn_tasks.publish_user_logged_in(
        message, app=app, **task_opts)


def call_publish_platform_create(
        instance: Platform,
        app: Celery = None,
        **task_opts):
    message = authn_pb2.Platform(
        id=instance.pk,
        subid=instance.subid,
        name=instance.name,
        type=instance.platform_type)
    return authn_tasks.publish_platform_create(
        message, app=app, **task_opts)


def call_publish_platform_update(
        instance: Platform,
        app: Celery = None,
        **task_opts):
    message = authn_pb2.Platform(
        id=instance.pk,
        subid=instance.subid,
        name=instance.name,
        type=instance.platform_type)
    return authn_tasks.publish_platform_update(
        message, app=app, **task_opts)


def call_publish_platform_delete(
        platform_id: int,
        app: Celery = None,
        **task_opts):
    message = authn_pb2.Platform(id=platform_id)
    return authn_tasks.publish_platform_delete(
        message, app=app, **task_opts)


def call_publish_session_create(
        instance: Session,
        app: Celery = None,
        **task_opts):
    message = authn_pb2.Session(
        id=instance.pk,
        subid=instance.subid,
        user_id=instance.user_id,
        platform_id=instance.platform_id,
        device_id=instance.device_id)
    return authn_tasks.publish_session_create(
        message, app=app, **task_opts)


def call_publish_session_delete(
        session_id: int,
        app: Celery = None,
        **task_opts):
    message = authn_pb2.Session(
        id=session_id)
    return authn_tasks.publish_session_delete(
        message, app=app, **task_opts)


def call_publish_account_create(
        instance: User,
        app: Celery = None,
        **task_opts):
    profile = instance.profile
    message = authn_pb2.Account(
        user=authn_pb2.User(
            id=instance.pk,
            subid=instance.subid,
            is_active=instance.is_active,
            is_staff=instance.is_staff,
            is_superuser=instance.is_superuser),
        profile=authn_pb2.UserProfile(
            user_id=profile.user_id,
            name=profile.name
        )
    )
    return authn_tasks.publish_account_create(
        message, app=app, **task_opts)


def call_publish_user_active_flag(
        instance: User,
        app: Celery = None,
        **task_opts):
    message = authn_pb2.UserActiveFlag(
        user_id=instance.pk,
        is_active=instance.is_active)
    return authn_tasks.publish_user_active_flag(
        message, app=app, **task_opts)


def call_publish_profile_update(
        instance: UserProfile,
        app: Celery = None,
        **task_opts):
    message = authn_pb2.UserProfile(
        user_id=instance.user_id,
        name=instance.name)
    return authn_tasks.publish_profile_update(
        message, app=app, **task_opts)
