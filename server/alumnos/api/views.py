from django.db.models.manager import BaseManager
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter

from server.alumnos.models import Alumno
from server.alumnos.models import Inhabilitacion
from server.alumnos.models import TipoEstado
from server.alumnos.models import TipoInhabilitacion
from server.alumnos.paginations import AlumnoResultsSetPagination

from .serializers import AlumnoCreateSerializer
from .serializers import AlumnoRetrieveSerializer
from .serializers import InhabilitacionSerializer
from .serializers import TipoEstadoSerializer
from .serializers import TipoInhabilitacionSerializer

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


class InhabilitacionViewSet(viewsets.ModelViewSet):
    queryset: BaseManager[Inhabilitacion] = Inhabilitacion.objects.all()
    serializer_class = InhabilitacionSerializer


class TipoInhabilitacionViewSet(viewsets.ModelViewSet):
    queryset: BaseManager[TipoInhabilitacion] = TipoInhabilitacion.objects.all()
    serializer_class = TipoInhabilitacionSerializer


class TipoEstadoViewSet(viewsets.ModelViewSet):
    queryset: BaseManager[TipoEstado] = TipoEstado.objects.all()
    serializer_class = TipoEstadoSerializer
