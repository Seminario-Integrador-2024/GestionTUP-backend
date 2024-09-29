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
import datetime

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



#http:/localhost:8080/alumnos/pagaron-cuota/<cuota_anio>/
class AlumnosQuePagaronCuotaViewSet(viewsets.ModelViewSet):
    pagination_class = AlumnoResultsSetPagination
    
    def get_queryset(self):
        # Este método es obligatorio para ModelViewSet, pero no lo utilizaremos en este caso.
        return Alumno.objects.none()

    def list(self, request, mes_anio=None):
        try:
            # Dividir el parámetro para obtener el número de cuota y el año
            mes, anio = map(int, mes_anio.split('-'))
        except ValueError:
            return Response({"error": "Formato inválido, debe ser <nro_cuota>-<año>"}, status=status.HTTP_400_BAD_REQUEST)

        # Definir el rango de meses para cuotas 1-10 (Marzo a Diciembre)
        if mes < 1 or mes > 12:
            return Response({"error": "El número de cuota debe estar entre 1 y 10."}, status=status.HTTP_400_BAD_REQUEST)

        # Mapear el número de cuota a un mes (cuota 1 -> Marzo, cuota 2 -> Abril, etc.)
        #mes = nro_cuota + 2  # Cuota 1 es marzo (mes 3)

        # Definir la fecha de inicio y fin para el mes y año proporcionados
        fecha_inicio = datetime.date(anio, mes, 1)
        ultimo_dia_mes = (fecha_inicio.replace(month=mes % 12 + 1, day=1) - datetime.timedelta(days=1)).day
        fecha_fin = datetime.date(anio, mes, ultimo_dia_mes)

        # Filtrar alumnos con estado académico activo
        alumnos_activos = Alumno.objects.filter(estado_academico="Activo")

        # Obtener cuotas que correspondan al mes y año proporcionados
        cuotas = Cuota.objects.filter(fecha_vencimiento__range=(fecha_inicio, fecha_fin))

        if not cuotas.exists():
            return Response({"error": "No existen cuotas para el mes y año especificados."}, status=status.HTTP_404_NOT_FOUND)

        # Obtener los IDs de las cuotas
        cuota_ids = cuotas.values_list('id_cuota', flat=True)

        # Filtrar alumnos que han pagado alguna de esas cuotas
        alumnos_con_pago = alumnos_activos.filter(
            cuota__lineadepago__cuota__id_cuota__in=cuota_ids, 
            pago__lineadepago__pago__estado="Confirmado"
        ).distinct()

        # Aplicar paginación
        page = self.paginate_queryset(alumnos_con_pago)
        if page is not None:
            serializer = AlumnosPagYNoCuotaSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Serializar los datos
        serializer = AlumnosPagYNoCuotaSerializer(alumnos_con_pago, many=True)
        return Response(serializer.data)



#http:/localhost:8080/alumnos/no-pagaron-cuota/<cuota_anio>/
class AlumnosQueNoPagaronCuotaViewSet(viewsets.ModelViewSet):

    pagination_class = AlumnoResultsSetPagination
    
    def get_queryset(self):
        # Este método es obligatorio para ModelViewSet, pero no lo utilizaremos en este caso.
        return Alumno.objects.none()

    def list(self, request, mes_anio=None):
        try:
            # Dividir el parámetro para obtener el número de cuota y el año
            mes, anio = map(int, mes_anio.split('-'))
        except ValueError:
            return Response({"error": "Formato inválido, debe ser <nro_cuota>-<año>"}, status=status.HTTP_400_BAD_REQUEST)

        # Definir el rango de meses para cuotas 1-10 (Marzo a Diciembre)
        if mes < 1 or mes > 12:
            return Response({"error": "El número de cuota debe estar entre 1 y 12."}, status=status.HTTP_400_BAD_REQUEST)

        # Mapear el número de cuota a un mes (cuota 1 -> Marzo, cuota 2 -> Abril, etc.)
        #mes = nro_cuota   # Cuota 1 es marzo (mes 3)

        # Definir la fecha de inicio y fin para el mes y año proporcionados
        fecha_inicio = datetime.date(anio, mes, 1)
        ultimo_dia_mes = (fecha_inicio.replace(month=mes % 12 + 1, day=1) - datetime.timedelta(days=1)).day
        fecha_fin = datetime.date(anio, mes, ultimo_dia_mes)

        # Filtrar alumnos con estado académico activo
        alumnos_activos = Alumno.objects.filter(estado_academico="Activo")

        # Obtener cuotas que correspondan al mes y año proporcionados
        cuotas = Cuota.objects.filter(fecha_vencimiento__range=(fecha_inicio, fecha_fin),
                                        estado__in = ["Vencida","Impaga","Pagada parcialmente"])
        if not cuotas.exists():
            return Response({"error": "No existen cuotas para el mes y año especificados."}, status=status.HTTP_404_NOT_FOUND)

        # Obtener los IDs de las cuotas
        cuota_ids = cuotas.values_list('id_cuota', flat=True)

        # Filtrar alumnos que han pagado alguna de esas cuotas
        # relacionar los alumnos_activos con sus cuotas sabiendo que cuotas tiene alumno_id
        alumnos_sin_pago = alumnos_activos.exclude(
            cuota__lineadepago__cuota__id_cuota__in=cuota_ids,
            pago__lineadepago__pago__estado="Confirmado"
        ).distinct()


        # Aplicar paginación
        page = self.paginate_queryset(alumnos_sin_pago)
        if page is not None:
            serializer = AlumnosPagYNoCuotaSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)


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
