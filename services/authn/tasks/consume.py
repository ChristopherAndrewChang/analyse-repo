from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from celery import current_app as celery_app

from idvalid_integration.protos.models import otp_pb2, tenant_pb2, rbac_pb2

from authn.models import (
    Enrollment,
    ForgetPassword,
    ChangeEmail,
    Tenant,
    TenantUser,
    RoleUser,
)
from authn.tasks import constants

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "consume_otp_publish_task",

    "consume_tenant_publish_task",
    "consume_tenant_user_publish_task",
    "consume_tenant_user_delete_task",

    "consume_rbac_role_user_create_task",
    "consume_rbac_role_user_delete_task",
)


@celery_app.task(
    name=constants.TASK_CONSUME_OTP_PUBLISH,
    queue=constants.QUEUE_CONSUME,
    shared=False)
def consume_otp_publish_task(message: bytes):
    message = otp_pb2.Otp.FromString(message)
    if message.usage == constants.OTP_USAGE_ENROLLMENT:
        instance = Enrollment.objects.get(
            subid=message.object_id)  # type: Enrollment
        instance.setup_token(
            message.id, message.token)
    elif message.usage == constants.OTP_USAGE_FORGET_PASSWORD:
        instance = ForgetPassword.objects.get(
            subid=message.object_id)  # type: ForgetPassword
        instance.setup_token(
            message.id, message.token)
    elif message.usage == constants.OTP_USAGE_CHANGE_EMAIL:
        instance = ChangeEmail.objects.get(
            subid=message.object_id)  # type: ChangeEmail
        instance.setup_token(message.id, message.token)


@celery_app.task(
    name=constants.TASK_CONSUME_TENANT_PUBLISH,
    queue=constants.QUEUE_CONSUME,
    shared=False)
def consume_tenant_publish_task(message: bytes):
    message = tenant_pb2.Tenant.FromString(message)
    Tenant.objects.create_or_update_from_message(message)


@celery_app.task(
    name=constants.TASK_CONSUME_TENANT_USER_PUBLISH,
    queue=constants.QUEUE_CONSUME,
    shared=False)
def consume_tenant_user_publish_task(message: bytes):
    message = tenant_pb2.TenantUser.FromString(message)
    TenantUser.objects.create_or_update_from_message(message)


@celery_app.task(
    name=constants.TASK_CONSUME_TENANT_USER_DELETE,
    queue=constants.QUEUE_CONSUME,
    shared=False)
def consume_tenant_user_delete_task(message: bytes):
    message = tenant_pb2.TenantUser.FromString(message)
    TenantUser.objects.delete_from_message(message)


@celery_app.task(
    name=constants.TASK_CONSUME_RBAC_ROLE_USER_CREATE,
    queue=constants.QUEUE_CONSUME,
    shared=False)
def consume_rbac_role_user_create_task(message: bytes):
    message = rbac_pb2.RoleUser.FromString(message)
    RoleUser.objects.create_or_update_from_message(message)


@celery_app.task(
    name=constants.TASK_CONSUME_RBAC_ROLE_USER_DELETE,
    queue=constants.QUEUE_CONSUME,
    shared=False)
def consume_rbac_role_user_delete_task(message: bytes):
    message = rbac_pb2.RoleUser.FromString(message)
    RoleUser.objects.delete_from_message(message)
