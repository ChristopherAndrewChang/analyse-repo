import preconf
from django.conf import settings
from kombu import Queue, Exchange, binding
from celery import Celery

from rbac.tasks import constants


exchange_publisher = Exchange(
    name=constants.EXCHANGE_PUBLISHER, type="topic")
exchange = Exchange(name=constants.EXCHANGE)
settings.CELERY_TASK_QUEUES = [
    Queue(
        name=constants.QUEUE_CONSUME,
        bindings=[
            # auth bindings
            binding(
                exchange=exchange_publisher,
                routing_key=constants.ROUTING_CONSUME_AUTH_ACCOUNT_CREATE),
            binding(
                exchange=exchange_publisher,
                routing_key=constants.ROUTING_CONSUME_AUTH_USER_ACTIVE_FLAG),
            binding(
                exchange=exchange_publisher,
                routing_key=constants.ROUTING_CONSUME_AUTH_PROFILE_UPDATE),

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
        ]
    ),
    Queue(
        name=constants.QUEUE_SIGNAL,
        bindings=[
            binding(
                exchange=exchange,
                routing_key=constants.ROUTING_SIGNAL),
        ]
    )
]
settings.CELERY_IMPORTS = []

app = Celery('rbac-service')
app.config_from_object('django.conf:settings', namespace='CELERY')
