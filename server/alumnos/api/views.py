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
from django.db.models import Q


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



#http:/localhost:8080/alumnos/pagaron-cuota/<mes_anio>/
class AlumnosQuePagaronCuotaViewSet(viewsets.ModelViewSet):
    pagination_class = AlumnoResultsSetPagination
    filter_backends = [OrderingFilter]  # Agregar el backend de ordenación
    ordering_fields = ['full_name']     # Especificar los campos por los que se puede ordenar
    ordering = ['full_name']            # Ordenar por defecto por 'full_name'

    
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
        cuotas = Cuota.objects.filter(fecha_vencimiento__range=(fecha_inicio, fecha_fin), 
                                        estado__in=["Pagada completamente"])

        if not cuotas.exists():
            return Response([], status=status.HTTP_200_OK)
            #return Response({"error": "No existen cuotas para el mes y año especificados."}, status=status.HTTP_404_NOT_FOUND)

        # Obtener los IDs de las cuotas
        cuota_ids = cuotas.values_list('id_cuota', flat=True)

        # Filtrar alumnos que han pagado alguna de esas cuotas
        alumnos_con_pago = alumnos_activos.filter(
            cuota__lineadepago__cuota__id_cuota__in=cuota_ids, 
            cuota__lineadepago__pago__estado = "Confirmado"
        ).order_by("user__full_name").distinct()

        # Aplicar paginación
        page = self.paginate_queryset(alumnos_con_pago)
        if page is not None:
            serializer = AlumnosPagYNoCuotaSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Serializar los datos
        serializer = AlumnosPagYNoCuotaSerializer(alumnos_con_pago, many=True)
        return Response(serializer.data)



#http:/localhost:8080/alumnos/no-pagaron-cuota/<mes_anio>/
class AlumnosQueNoPagaronCuotaViewSet(viewsets.ModelViewSet):

    pagination_class = AlumnoResultsSetPagination
    filter_backends = [OrderingFilter]  # Agregar el backend de ordenación
    ordering_fields = ['full_name']     # Especificar los campos por los que se puede ordenar
    ordering = ['full_name']            # Ordenar por defecto por 'full_name'


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
        cuotas = Cuota.objects.filter(
            fecha_vencimiento__range=(fecha_inicio, fecha_fin),
            alumno__in=alumnos_activos)

        print("$$$$$$$$$$$$$$$$$$$$$ cuotas",cuotas[0].id_cuota, cuotas[1].id_cuota,cuotas[2].id_cuota)
        if not cuotas.exists():
            return Response({"error": "No existen cuotas para el mes y año especificados."}, status=status.HTTP_404_NOT_FOUND)

        # Obtener los IDs de las cuotas
        cuota_ids = cuotas.values_list('id_cuota', flat=True)
        print("$$$$$$$$$$$$$$$$$$$$$ cuota_ids",cuota_ids)

        # Obtener los alumnos que han pagado completamente las cuotas con pagos confirmados
        alumnos_con_pago_confirmado = alumnos_activos.filter(
            Q(cuota__id_cuota__in=cuota_ids) &  # Cuotas 6 y 12
            Q(cuota__estado__in=["Pagada completamente","Pagada parcialmente"]) &  # Estado de la cuota
            Q(cuota__lineadepago__pago__estado="Confirmado")  # Pago confirmado para la cuota en cuestión
        ).distinct()

        # Verifica cuántos alumnos han pagado completamente
        print("Alumnos con pago confirmado:", alumnos_con_pago_confirmado.count())

        # Filtrar alumnos que no han pagado la cuota 1-2025
        alumnos_sin_pago = alumnos_activos.exclude(
            # Excluir alumnos que han pagado completamente las cuotas 6 y 12
            Q(user__in=alumnos_con_pago_confirmado.values_list('user', flat=True))
        ).exclude(
            # Excluir cuotas que están "Pagadas parcialmente" sin importar el estado de los pagos
            Q(cuota__id_cuota__in=cuota_ids) &  # Cuotas 6 y 12
            Q(cuota__estado__in="Pagada parcialmente")  # Solo estado de la cuota
        ).order_by("user__full_name").distinct()

        # Verifica cuántos alumnos quedan sin pago
        print("Alumnos sin pago:", alumnos_sin_pago.count())



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
