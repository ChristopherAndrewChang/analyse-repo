from django.apps import AppConfig


class MailerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mailer'

    def ready(self) -> None:
        if not getattr(self, "_ready_passed", False):
            self.register_signal()
            setattr(self, "_ready_passed", True)

    def register_signal(self) -> None:
        from mailer import receivers
