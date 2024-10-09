# core/models/modelo_alumno.py

# django imports


from datetime import datetime

from django.db import models
from django.utils.translation import gettext_lazy as _

from server.users.models import User

# Create your models here.

choices_fin = (
    ("Habilitado", "Habilitado"),
    ("Inhabilitado", "Inhabilitado"),
)
choices_acad = (
    ("Activo", "Activo"),
    ("Inactivo", "Inactivo"),
)
current_year = datetime.now().year
last_year = (
    ("1C-" + str(current_year), "1C-" + str(current_year)),
    ("2C-" + str(current_year), "2C-" + str(current_year)),
)


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
    estado_financiero = models.CharField(choices=choices_fin, default="Habilitado")
    estado_academico = models.CharField(choices=choices_acad, default="Activo")
    legajo = models.PositiveIntegerField(_("Legajo"), unique=True, default=0)
    anio_ingreso = models.IntegerField()
    telefono = models.CharField(blank=True)
    tel_res = models.CharField(blank=True)
    ultimo_cursado = models.CharField(
        auto_created=True,
        default=last_year[0][0],
        choices=last_year,
    )
    celular = models.CharField(blank=True)
    gender = models.CharField(
        max_length=1,
        choices=(("M", "male"), ("F", "female")),
        default="M",
    )

    def __str__(self) -> str:
        return self.user.full_name

    def __repr__(self) -> str:
        return __str__()

    def __unicode__(self):
        return "%i" % self.user.dni

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
    fecha_desde = models.DateTimeField()
    fecha_hasta = models.DateTimeField(blank=True, null=True)
    descripcion = models.TextField()
    fecha_hasta = models.DateTimeField()
    descripcion = models.TextField()

    # fecha desde y id alumno clave primaria compuesta
    def __str__(self) -> str:
        return super().__str__()


class Rehabilitados(models.Model):
    """
    Represents a student who has been rehabilitated after up to date payment installment.

    Args:
        Alumno (type): The Alumno model.

    Attributes:
        user (OneToOneField): The user associated with the student.
        fecha_deshabilitacion (DateTimeField): The date and time of the student was inhabilitated.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        to_field="dni",
        default=0,
        primary_key=True,
    )
    estado = models.CharField(choices=choices_fin, default="Rehabilitado")
    legajo = models.ForeignKey(Alumno, to_field="legajo", on_delete=models.DO_NOTHING)
    fecha_rehabilitacion = models.DateTimeField(
        auto_now_add=True,
    )
    fecha_deshabilitacion = models.DateTimeField(null=True, blank=False)

    def __str__(self) -> str:
        return super().__str__()
