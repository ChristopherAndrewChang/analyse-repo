from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from idvalid_integration.tasks import constants, call_task

if TYPE_CHECKING:
    from celery import Celery
    from idvalid_integration.protos.models import authn_pb2


logger = logging.getLogger(__name__)
__all__ = (
    "session_revoke",

    "publish_user_logged_in",

    "publish_platform_create",
    "publish_platform_update",
    "publish_platform_delete",

    "publish_session_create",
    "publish_session_delete",

    "publish_account_create",
    "publish_user_active_flag",
    "publish_profile_update",
)


def session_revoke(
        message: authn_pb2.Session, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_EXTERNAL_AUTH_SESSION_REVOKE,
        app=app,
        args=(message.SerializeToString(deterministic=True),),
        argsrepr="authn_pb2.Session message",
        exchange=constants.EXCHANGE_AUTH,
        routing_key=constants.ROUTING_AUTH_EXTERNAL,
        **task_opts)


def publish_user_logged_in(
        message: authn_pb2.UserLoggedIn, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_CONSUME_AUTH_USER_LOGGED_IN,
        app=app,
        args=(message.SerializeToString(deterministic=True),),
        argsrepr="authn_pb2.UserLoggedIn message",
        exchange=constants.EXCHANGE_PUBLISHER,
        routing_key=f"{constants.ROUTING_AUTH_PUBLISH_PREFIX}.logged-in",
        **task_opts)


def publish_platform_create(
        message: authn_pb2.Platform, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_CONSUME_AUTH_PLATFORM_CREATE,
        app=app,
        args=(message.SerializeToString(deterministic=True),),
        argsrepr="authn_pb2.Platform message",
        exchange=constants.EXCHANGE_PUBLISHER,
        routing_key=(
            f"{constants.ROUTING_AUTH_PLATFORM_PUBLISH_PREFIX}.create"),
        **task_opts)


def publish_platform_update(
        message: authn_pb2.Platform, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_CONSUME_AUTH_PLATFORM_UPDATE,
        app=app,
        args=(message.SerializeToString(deterministic=True),),
        argsrepr="authn_pb2.Platform message",
        exchange=constants.EXCHANGE_PUBLISHER,
        routing_key=(
            f"{constants.ROUTING_AUTH_PLATFORM_PUBLISH_PREFIX}.update"),
        **task_opts)


def publish_platform_delete(
        message: authn_pb2.Platform, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_CONSUME_AUTH_PLATFORM_DELETE,
        app=app,
        args=(message.SerializeToString(deterministic=True),),
        argsrepr="authn_pb2.Platform message",
        exchange=constants.EXCHANGE_PUBLISHER,
        routing_key=(
            f"{constants.ROUTING_AUTH_PLATFORM_PUBLISH_PREFIX}.delete"),
        **task_opts)


def publish_session_create(
        message: authn_pb2.Session, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_CONSUME_AUTH_SESSION_CREATE,
        app=app,
        args=(message.SerializeToString(deterministic=True),),
        argsrepr="authn_pb2.Session message",
        exchange=constants.EXCHANGE_PUBLISHER,
        routing_key=(
            f"{constants.ROUTING_AUTH_SESSION_PUBLISH_PREFIX}.create"),
        **task_opts)


def publish_session_delete(
        message: authn_pb2.Session, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_CONSUME_AUTH_SESSION_DELETE,
        app=app,
        args=(message.SerializeToString(deterministic=True),),
        argsrepr="authn_pb2.Session message",
        exchange=constants.EXCHANGE_PUBLISHER,
        routing_key=(
            f"{constants.ROUTING_AUTH_SESSION_PUBLISH_PREFIX}.delete"),
        **task_opts)


def publish_account_create(
        message: authn_pb2.Account, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_CONSUME_AUTH_ACCOUNT_CREATE,
        app=app,
        args=(message.SerializeToString(deterministic=True),),
        argsrepr="authn_pb2.Account message",
        exchange=constants.EXCHANGE_PUBLISHER,
        routing_key=(
            f"{constants.ROUTING_AUTH_ACCOUNT_PUBLISH_PREFIX}.create"),
        **task_opts)


def publish_user_active_flag(
        message: authn_pb2.UserActiveFlag, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_CONSUME_AUTH_USER_ACTIVE_FLAG,
        app=app,
        args=(message.SerializeToString(deterministic=True),),
        argsrepr="authn_pb2.UserActiveFlag message",
        exchange=constants.EXCHANGE_PUBLISHER,
        routing_key=(
            f"{constants.ROUTING_AUTH_USER_PUBLISH_PREFIX}.active-flag"),
        **task_opts)


def publish_profile_update(
        message: authn_pb2.UserProfile, *,
        app: Celery = None,
        **task_opts):
    return call_task(
        constants.TASK_CONSUME_AUTH_PROFILE_UPDATE,
        app=app,
        args=(message.SerializeToString(deterministic=True),),
        argsrepr="authn_pb2.UserProfile message",
        exchange=constants.EXCHANGE_PUBLISHER,
        routing_key=(
            f"{constants.ROUTING_AUTH_PROFILE_PUBLISH_PREFIX}.update"),
        **task_opts)
