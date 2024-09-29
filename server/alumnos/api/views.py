from django.db.models.manager import BaseManager
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter

from server.alumnos.models import Alumno
from server.alumnos.models import Inhabilitacion
from server.alumnos.models import TipoEstado
from server.alumnos.models import TipoInhabilitacion
from server.materias.models import Materia
from server.alumnos.paginations import AlumnoResultsSetPagination

from server.pagos.models import Cuota

from .serializers import AlumnoCreateSerializer
from .serializers import AlumnoRetrieveSerializer
from .serializers import InhabilitacionSerializer
from .serializers import TipoEstadoSerializer
from .serializers import TipoInhabilitacionSerializer
from .serializers import AlumnosPagYNoCuotaSerializer

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


#http:/localhost:8080/alumnos/pagaron-cuota/<nro_cuota>/
class AlumnosQuePagaronCuotaViewSet(viewsets.ModelViewSet):
    pagination_class = AlumnoResultsSetPagination

    def list(self, request, nro_cuota=None):
        # Filtrar alumnos con estado académico activo
        alumnos_activos = Alumno.objects.filter(estado_academico="Activo")

        # Obtener todas las cuotas que tengan el mismo nro_cuota
        cuotas = Cuota.objects.filter(nro_cuota=nro_cuota)

        if not cuotas.exists():
            return Response({"error": "No existen cuotas con el número especificado."}, status=status.HTTP_404_NOT_FOUND)

        # Obtener los IDs de las cuotas
        cuota_ids = cuotas.values_list('id_cuota', flat=True)

        # Obtener alumnos que hayan pagado alguna de esas cuotas específicas
        alumnos_con_pago = alumnos_activos.filter(
            cuota__lineadepago__cuota__id_cuota__in=cuota_ids, 
            pago__lineadepago__pago__estado ="Confirmado"
        ).distinct()

        # Serializar los datos
        serializer = AlumnosPagYNoCuotaSerializer(alumnos_con_pago, many=True)
        return Response(serializer.data)



#http:/localhost:8080/alumnos/no-pagaron-cuota/<nro_cuota>/
class AlumnosQueNoPagaronCuotaViewSet(viewsets.ModelViewSet):
    pagination_class = AlumnoResultsSetPagination

    def list(self, request, nro_cuota=None):
        # Filtrar alumnos con estado académico activo
        alumnos_activos = Alumno.objects.filter(estado_academico="Activo")

        alumnos_firm_compdepag = alumnos_activos.filter(firmacomppagoalumno__firmado=True)

        # Obtener todas las cuotas que tengan el mismo nro_cuota
        cuotas = Cuota.objects.filter(nro_cuota=nro_cuota)

        if not cuotas.exists():
            return Response({"error": "No existen cuotas con el número especificado."}, status=status.HTTP_404_NOT_FOUND)

        # Obtener los IDs de las cuotas
        cuota_ids = cuotas.values_list('id_cuota', flat=True)

        # Obtener alumnos que NO hayan pagado ninguna de esas cuotas
        alumnos_sin_pago = alumnos_firm_compdepag.exclude(
            cuota__lineadepago__cuota__id_cuota__in=cuota_ids, 
            pago__lineadepago__pago__estado="Informado"
        ).distinct()

        # Serializar los datos
        serializer = AlumnosPagYNoCuotaSerializer(alumnos_sin_pago, many=True)
        return Response(serializer.data)





class InhabilitacionViewSet(viewsets.ModelViewSet):
    queryset: BaseManager[Inhabilitacion] = Inhabilitacion.objects.all()
    serializer_class = InhabilitacionSerializer


class TipoInhabilitacionViewSet(viewsets.ModelViewSet):
    queryset: BaseManager[TipoInhabilitacion] = TipoInhabilitacion.objects.all()
    serializer_class = TipoInhabilitacionSerializer


class TipoEstadoViewSet(viewsets.ModelViewSet):
    queryset: BaseManager[TipoEstado] = TipoEstado.objects.all()
    serializer_class = TipoEstadoSerializer
