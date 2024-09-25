
from django.apps import AppConfig
from django.db.models.signals import post_migrate

class AlumnosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "server.alumnos"

    def ready(self):
        try:
            import server.alumnos.signals  # noqa: F401
        except ImportError:
            pass

        from server.users.permissions import setup_groups_and_permissions
        post_migrate.connect(setup_groups_and_permissions, sender=self)
