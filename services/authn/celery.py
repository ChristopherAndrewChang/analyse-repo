import preconf
from django.conf import settings
from kombu import Queue, Exchange, binding
from celery import Celery

from .tasks import constants


exchange_publisher = Exchange(
    name=constants.EXCHANGE_PUBLISHER, type="topic")
exchange = Exchange(
    name=constants.EXCHANGE, type="direct")
settings.CELERY_TASK_QUEUES = [
    Queue(
        name=constants.QUEUE_CONSUME,
        bindings=[
            # otp bindings
            binding(
                exchange=exchange_publisher,
                routing_key=constants.ROUTING_CONSUME_OTP_PUBLISH_ENROLLMENT),
            binding(
                exchange=exchange_publisher,
                routing_key=constants.ROUTING_CONSUME_OTP_PUBLISH_FORGET_PASSWORD),
            binding(
                exchange=exchange_publisher,
                routing_key=constants.ROUTING_CONSUME_OTP_PUBLISH_CHANGE_EMAIL),

            # tenant bindings
            binding(
                exchange=exchange_publisher,
                routing_key=constants.ROUTING_CONSUME_TENANT_PUBLISH),
            binding(
                exchange=exchange_publisher,
                routing_key=constants.ROUTING_CONSUME_TENANT_USER_PUBLISH),
            binding(
                exchange=exchange_publisher,
                routing_key=constants.ROUTING_CONSUME_TENANT_USER_DELETE),

            # rbac bindings
            binding(
                exchange=exchange_publisher,
                routing_key=constants.ROUTING_CONSUME_RBAC_ROLE_USER_CREATE),
            binding(
                exchange=exchange_publisher,
                routing_key=constants.ROUTING_CONSUME_RBAC_ROLE_USER_DELETE),
        ]
    ),
    Queue(
        name=constants.QUEUE_EXTERNAL,
        bindings=[
            binding(
                exchange=exchange,
                routing_key=constants.ROUTING_EXTERNAL),
        ]
    ),
    Queue(
        name=constants.QUEUE_SIGNAL,
        bindings=[
            binding(
                exchange=exchange,
                routing_key=constants.ROUTING_SIGNAL)
        ]
    )
]
settings.CELERY_IMPORTS = []

app = Celery('authn-service')
app.config_from_object(
    'django.conf:settings', namespace='CELERY')
