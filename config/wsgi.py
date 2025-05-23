"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import preconf
from config import celery

from django.core.wsgi import get_wsgi_application


application = get_wsgi_application()
