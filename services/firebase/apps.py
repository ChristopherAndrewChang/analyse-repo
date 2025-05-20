from __future__ import annotations

import firebase_admin
from firebase_admin import credentials

from django.apps import AppConfig

from firebase.settings import firebase_settings


class FirebaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'firebase'

    def ready(self):
        if key_file := firebase_settings.KEY_JSON_FILE:
            cred = credentials.Certificate(key_file)
            firebase_admin.initialize_app(cred)
