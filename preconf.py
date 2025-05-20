import os
from modules.idvalid_integration.tasks import serialization  # noqa


os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE', 'config.settings')
