import preconf
from django.conf import settings
from kombu import Queue, Exchange, binding
from celery import Celery

from .tasks import constants


exchange = Exchange(
    name=constants.EXCHANGE, type="direct")
publisher_exchange = Exchange(
    name=constants.EXCHANGE_PUBLISHER, type="topic")
settings.CELERY_TASK_QUEUES = [
    Queue(
        name=constants.QUEUE_CONSUME,
        bindings=[
            binding(
                exchange=publisher_exchange,
                routing_key=constants.ROUTING_CONSUME_OTP_PUBLISH),
            binding(
                exchange=publisher_exchange,
                routing_key=constants.ROUTING_CONSUME_OTP_APPLY),
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

app = Celery('enrollment-service')
app.config_from_object(
    'django.conf:settings', namespace='CELERY')
