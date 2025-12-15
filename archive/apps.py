from django.apps import AppConfig


class ArchiveConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "archive"

    def ready(self):
        # импортируем сигналы при старте приложения
        import archive.signals