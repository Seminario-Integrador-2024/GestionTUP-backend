from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import User


@receiver(signal=[post_migrate])
def post_migrate_create_superuser(sender, **kwargs):
    if not User.objects.filter(is_superuser=True).exists():
        User.objects.create_superuser(
            # username=None,
            dni=12345678,
            email="admin@admin.com",
            password="admin",
        )

        # check for all users without a group
        x = 0
        while not User.objects.filter(groups=None).exists() and x < 1000:
            User.objects.update(groups=Group.objects.get_or_create(name="Usuarios")[0])
            x += 1
