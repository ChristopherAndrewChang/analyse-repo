from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from twilio.rest import Client

from idvalid_integration.tasks import (
    otp as otp_tasks,
)
from idvalid_integration.protos.models import (
    otp_pb2,
)

from authn.tasks import constants

if TYPE_CHECKING:
    from celery import Celery
    from authn.models import Enrollment, ForgetPassword, ChangeEmail


logger = logging.getLogger(__name__)
__all__ = (
    "call_external_enrollment_otp_create",
    "call_external_forget_password_otp_create",
    "call_external_change_email_otp_create",
)


def call_external_enrollment_otp_create(
        instance: Enrollment, *,
        app: Celery = None,
        **task_opts):
    if instance.email_id:
        params = {
            "method": otp_pb2.Method.METHOD_MAIL,
            "ref_id": instance.email.subid,
            "email_address": instance.email.address
        }
    elif instance.phone_id:
        params = {
            "method": otp_pb2.Method.METHOD_SMS,
            "ref_id": instance.phone.subid,
            "phone_number": instance.phone.number.as_e164
        }
    else:
        raise ValueError("unknown email or phone must be set")
    message = otp_pb2.CreateOtp(
        object_id=instance.subid,
        usage=constants.OTP_USAGE_ENROLLMENT,
        device_id=instance.device_id,
        user_agent=instance.user_agent,
        **params)
    return otp_tasks.create(message, app=app, **task_opts)


def call_external_forget_password_otp_create(
        instance: ForgetPassword, *,
        app: Celery = None,
        **task_opts):
    message = otp_pb2.CreateOtp(
        object_id=instance.subid,
        usage=constants.OTP_USAGE_FORGET_PASSWORD,
        ref_id=instance.user.subid,
        method=otp_pb2.Method.METHOD_MAIL,
        device_id=instance.device_id,
        user_agent=instance.user_agent,
        email_address=instance.user.email)
    return otp_tasks.create(message, app=app, **task_opts)


def call_external_change_email_otp_create(
        instance: ChangeEmail, *,
        app: Celery = None,
        **task_opts):
    message = otp_pb2.CreateOtp(
        object_id=instance.subid,
        usage=constants.OTP_USAGE_CHANGE_EMAIL,
        ref_id=instance.user.subid,
        method=otp_pb2.Method.METHOD_MAIL,
        device_id=instance.device_id,
        user_agent=instance.user_agent,
        email_address=instance.email,
        owner_id=instance.user_id)
    return otp_tasks.create(message, app=app, **task_opts)