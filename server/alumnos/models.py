# core/models/modelo_alumno.py

# django imports

from django.contrib.auth.models import Group
from django.db import models
from django.db.models.signals import pre_save
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from server.users.models import User

# Create your models here.


class Alumno(models.Model):
    """
    Represents a student.

    Args:
        models (type): The Django models module.

    Attributes:
        user (OneToOneField): The user associated with the student.
        estado (CharField): The state of the student.
        legajo (PositiveIntegerField): The student's registration number.
        anio_ingreso (IntegerField): The year the student started.
        telefono (IntegerField): The student's phone number.
        celular (IntegerField): The student's cell phone number.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        to_field="dni",
        default=0,
        primary_key=True,
    )
    estado = models.CharField(max_length=255)
    legajo = models.PositiveIntegerField(_("Legajo"), unique=True, default=0)
    anio_ingreso = models.IntegerField()
    telefono = models.CharField(blank=True)
    tel_res = models.CharField(blank=True)
    celular = models.CharField(blank=True)
    gender = models.CharField(
        max_length=1,
        choices=(("M", "male"), ("F", "female")),
        default="M",
    )

    def __str__(self) -> str:
        return super().__str__()

    def __unicode__(self):
        return self.user.dni

    def get_cuil(self, dni, gender):
        s = ""
        if "m" in self.gender.lower():
            s += "20"
        else:
            s += "27"
        s += "-"
        s += str(dni)
        s += "-"
        s += "0"
        return s

    @property
    def cuil(self):
        return self.get_cuil(self.user.dni, self.gender)

    @property
    def user__dni(self):
        return self.user.dni


@receiver([pre_save], sender=Alumno)
def alumno_pre_save(sender, instance, **kwargs):
    """
    alumno_pre_save add alumno to Alumnos group.

    Args:
        sender (Alumno): The Alumno model.
        instance (Alumno): The instance of the Alumno model.
        created (bool): True if the instance was created, False otherwise.
        **kwargs: Arbitrary keyword arguments.
    """
    try:
        Group.objects.get(name="Alumnos")
    except Group.DoesNotExist:
        Group.objects.create(name="Alumnos")
    instance.user.groups.add(Group.objects.get(name="Alumnos"))


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
    if user_instance.groups.filter(name="Alumnos").exists():
        user_instance.groups.remove("Alumnos")


class Inhabilitacion(models.Model):
    """
    Represents an Inhabilitacion.

    Args:
        models (type): The Django models module.

    Attributes:
        id_alumno (ForeignKey): The foreign key to the Alumno model.
        id_tipo_inhabilitacion (ForeignKey): The foreign key to \
            the TipoInhabilitacion model.
        fecha_desde (DateTimeField): The starting date and time of \
            the inhabilitacion.
        fecha_hasta (DateTimeField): The ending date and time of \
            the inhabilitacion.
        descripcion (TextField): The description of the inhabilitacion.
    """

    id_alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    id_tipo_inhabilitacion = models.ForeignKey(
        "TipoInhabilitacion",
        on_delete=models.CASCADE,
    )
    fecha_desde = models.DateTimeField()
    fecha_hasta = models.DateTimeField()
    descripcion = models.TextField()

    def __str__(self) -> str:
        return super().__str__()


class TipoInhabilitacion(models.Model):
    """
    TipoInhabilitacion represents a type of disqualification.

    Args:
        models (django.db.models.Model): The base model class for \
            all Django models.
    """

    id_tipo_inhabilitacion = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()

    def __str__(self) -> str:
        return super().__str__()


class TipoEstado(models.Model):
    """
    Represents a type of state.

    Attributes:
        id_tipo_estado (AutoField): The primary key for \
            the TipoEstado instance.
        nombre (CharField): The name of the TipoEstado.
        descripcion (TextField): The description of the TipoEstado.
    """

    id_tipo_estado = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()

    def __str__(self) -> str:
        return super().__str__()
