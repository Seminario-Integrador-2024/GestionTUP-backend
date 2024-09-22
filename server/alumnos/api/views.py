from django.db.models.manager import BaseManager
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter

from server.alumnos.models import Alumno
from server.alumnos.models import Inhabilitacion
from server.alumnos.models import TipoEstado
from server.alumnos.models import TipoInhabilitacion
from server.materias.models import Materia
from server.alumnos.paginations import AlumnoResultsSetPagination

from .serializers import AlumnoCreateSerializer
from .serializers import AlumnoRetrieveSerializer
from .serializers import InhabilitacionSerializer
from .serializers import TipoEstadoSerializer
from .serializers import TipoInhabilitacionSerializer

from rest_framework import status
from .serializers import MateriaSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
# Create your views her


class AlumnosViewSet(viewsets.ModelViewSet):
    lookup_field = "user__dni"
    queryset: BaseManager[Alumno] = Alumno.objects.all()
    pagination_class = AlumnoResultsSetPagination
    filter_backends = [OrderingFilter]

    def get_serializer_class(self):
        # Usar el serializador adecuado según el método HTTP
        if (
            self.request.method == "GET"
            and self.action == "retrieve"
            or self.request.method == "GET"
            and self.action == "list"
        ):
            return AlumnoRetrieveSerializer
        return AlumnoCreateSerializer

    @action(detail=False, methods=['get'], url_path='materias/(?P<user_id>[^/.]+)')
    def materias(self, request, user_id=None):
        try:
            # Obtener el alumno por el user_id (dni)
            alumno = Alumno.objects.get(user__dni=user_id)
            # Obtener las materias relacionadas con el alumno
            materias_alumno = Materia.objects.filter(materiaalumno__id_alumno=alumno)
            # Serializar las materias
            serializer = MateriaSerializer(materias_alumno, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Alumno.DoesNotExist:
            return Response({'error': 'Alumno not found'}, status=status.HTTP_404_NOT_FOUND)


class InhabilitacionViewSet(viewsets.ModelViewSet):
    queryset: BaseManager[Inhabilitacion] = Inhabilitacion.objects.all()
    serializer_class = InhabilitacionSerializer


class TipoInhabilitacionViewSet(viewsets.ModelViewSet):
    queryset: BaseManager[TipoInhabilitacion] = TipoInhabilitacion.objects.all()
    serializer_class = TipoInhabilitacionSerializer


class TipoEstadoViewSet(viewsets.ModelViewSet):
    queryset: BaseManager[TipoEstado] = TipoEstado.objects.all()
    serializer_class = TipoEstadoSerializer
