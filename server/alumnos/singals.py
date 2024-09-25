from django.contrib.auth.models import Group
from django.db.models.signals import post_init
from django.db.models.signals import post_save
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import Alumno

"""
Signals for Alumno model.

"""


@receiver([post_save, post_init], sender=Alumno)
def alumno_post_save(sender, instance, created, **kwargs):
    """
    alumno_pre_save add alumno to Alumnos group.

    Args:
        sender (Alumno): The Alumno model.
        instance (Alumno): The instance of the Alumno model.
        created (bool): True if the instance was created, False otherwise.
        **kwargs: Arbitrary keyword arguments.
    """
    if created:
        alumno_group = Group.objects.get_or_create(name="Alumnos")
        instance.user.groups.add(alumno_group)


@receiver(pre_delete, sender=Alumno)
def alumno_pre_delete(sender, instance, **kwargs):
    """
    alumno_pre_delete remove alumno from Alumnos group.

    Args:
        sender (Alumno): The Alumno model.
        instance (Alumno): The instance of the Alumno model.
        **kwargs: Arbitrary keyword arguments.
    """
    user_instance = instance.user
    if user_instance.groups.filter(name="Alumnos").exists():
        user_instance.groups.remove("Alumnos")
