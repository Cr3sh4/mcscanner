from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app"

    # Background scheduler
    def ready(self):
        from .scheduler import start_scheduler
        start_scheduler()
