from django.shortcuts import render
from django.db.models.manager import BaseManager
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..models import Materia, MateriaAlumno, Alumno
from .serializers import MateriaSerializer, MateriaAlumnoSerializer

from django.shortcuts import render
from django.db.models.manager import BaseManager
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .serializers import MateriaSerializer, AlumnoSerializer
from rest_framework.permissions import AllowAny
from server.materias.paginations import MateriasAlumnoResultsSetPagination

# Create your views here.
class MateriaViewSet(viewsets.ModelViewSet):
    pagination_class = MateriasAlumnoResultsSetPagination
    lookup_field = 'codigo_materia'
    queryset: BaseManager[Materia] = Materia.objects.all()
    serializer_class = MateriaSerializer

class MateriaAlumnoViewSet(viewsets.ModelViewSet):
    queryset: BaseManager[MateriaAlumno] =  MateriaAlumno.objects.all()
    serializer_class = MateriaAlumnoSerializer
    pagination_class = MateriasAlumnoResultsSetPagination

class MateriaViewSet(viewsets.ModelViewSet):
    pagination_class = MateriasAlumnoResultsSetPagination
    lookup_field = 'codigo_materia'
    queryset: BaseManager[Materia] = Materia.objects.all()
    serializer_class = MateriaSerializer



    @action(detail=True, methods=['get'], url_path='alumnos')
    def alumnos(self, request, codigo_materia=None):
        try:
            materia = self.get_object()
            alumnos_relacionados = Alumno.objects.filter(materiaalumno__id_materia=materia)
            serializer = AlumnoSerializer(alumnos_relacionados, many=True)

            # Aplicar paginación
            page = self.paginate_queryset(alumnos_relacionados)
            if page is not None:
                serializer = AlumnoSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Materia.DoesNotExist:
            return Response({'error': 'Materia not found'}, status=status.HTTP_404_NOT_FOUND)

   