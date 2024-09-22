from django.core.files.base import ContentFile

#  third party imports
from rest_framework import serializers


#  custom imports
from ..models import *

class MateriaAlumnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MateriaAlumno
        fields = "__all__"

class AlumnoSerializer(serializers.ModelSerializer):
    dni = serializers.IntegerField(source="user.dni", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    class Meta:
        model = Alumno
        fields = [
            "dni", 
            "email", 
            "full_name", 
            "legajo", 
            "estado", 
            "anio_ingreso", 
            "telefono", 
            "tel_res", 
            "celular", 
            "gender"
        ]

class MateriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Materia
        fields = "__all__"

