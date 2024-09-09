from django.shortcuts import render
from django.db.models.manager import BaseManager
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..models import Materia, MateriaAlumno
from .serializers import MateriaSerializer, MateriaAlumnoSerializer

# Create your views here.
class MateriaViewSet(viewsets.ModelViewSet):
    lookup_field = 'codigo_materia'
    queryset: BaseManager[Materia] = Materia.objects.all()
    serializer_class = MateriaSerializer

class MateriaAlumnoViewSet(viewsets.ModelViewSet):
    queryset: BaseManager[MateriaAlumno] =  MateriaAlumno.objects.all()
    serializer_class = MateriaAlumnoSerializer






    
