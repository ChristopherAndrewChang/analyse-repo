from django.apps import AppConfig


class AuthnConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authn'

    def ready(self):
        from . import receivers
