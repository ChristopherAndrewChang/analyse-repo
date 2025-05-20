import preconf
from django.conf import settings
from kombu import Queue, Exchange, binding
from celery import Celery


settings.INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django_celery_results",
    "mailer",
]

# settings.DATABASE_ROUTERS = [
#     "chat_service.db_routers.ChatRouter"
# ]

settings.ROOT_URLCONF = None

esl_exchange = Exchange(name="esl", type="direct")
settings.CELERY_TASK_QUEUES = (
    Queue(name="mailer", bindings=[
        binding(
            exchange=esl_exchange,
            routing_key="mailer.internal"
        )
    ]),
)
settings.CELERY_IMPORTS = []

app = Celery('mailer-service')
app.config_from_object('django.conf:settings', namespace='CELERY')
