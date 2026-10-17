from django.apps import AppConfig

class VideosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'videoflix.apps.videos'
    verbose_name = 'Videos'

    def ready(self):
        # Registriert die Signal-Handler für die Video-Verarbeitung.
        from . import signals  # noqa: F401
