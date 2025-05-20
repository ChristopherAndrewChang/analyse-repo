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
            binding(
                exchange=exchange_publisher,
                routing_key=constants.ROUTING_CONSUME_ENROLLMENT),
            binding(
                exchange=exchange_publisher,
                routing_key=constants.ROUTING_CONSUME_OTP_PUBLISH),
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

app = Celery('account-service')
app.config_from_object(
    'django.conf:settings', namespace='CELERY')
