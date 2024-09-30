from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User


@receiver(signal=[post_migrate])
def post_migrate_create_superuser(sender, **kwargs):
    if not User.objects.filter(is_superuser=True).exists():
        User.objects.create_superuser(
            full_name="Admin",
            # username=None,
            dni=12345678,
            email="admin@admin.com",
            password="admin",
        )


@receiver(signal=[post_save], sender=User)
def post_save_user(sender, instance, created, **kwargs):
    if created:

        group_name = "Alumnos"
        if instance.is_superuser or instance.is_staff:
            group_name = "Administradores"
        group, _ = Group.objects.get_or_create(name=group_name)
        instance.groups.add(group)
        instance.save()
