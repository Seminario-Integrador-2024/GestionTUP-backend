# django imports
from django.db.models.manager import BaseManager
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.filters import OrderingFilter
from rest_framework.decorators import action
from rest_framework import viewsets
from django.http import FileResponse
import os


from rest_framework.decorators import parser_classes
from rest_framework.parsers import MultiPartParser, FormParser

from rest_framework.filters import OrderingFilter

# third party imports
from .serializers import *
from ..paginations import *
#utils imports
from ..utils import generar_cuotas

class PagoViewSet(viewsets.ModelViewSet):
    queryset : BaseManager[Pago] = Pago.objects.all()
    serializer_class = PagoSerializer
    pagination_class = PagoResultsSetPagination


from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

class PagoDeUnAlumnoRetrieveViewSet(viewsets.ModelViewSet):
    serializer_class = PagoDeUnAlumnoRetrieveSerializer
    pagination_class = PagoResultsSetPagination

    def get_queryset(self):

        return Pago.objects.all()

    def list(self, request, alumno_id=None):
        if alumno_id is None:
            return Response({"detail": "Alumno ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Filtrar los pagos por el ID del alumno
        pagos = self.get_queryset().filter(alumno=alumno_id)

        if not pagos.exists():
            return Response({"detail": "No payments found for this student."}, status=status.HTTP_404_NOT_FOUND)

        # Aplicar paginación
        paginator = self.pagination_class()
        paginated_pagos = paginator.paginate_queryset(pagos, request)

        # Serializar los pagos paginados
        serializer = self.serializer_class(paginated_pagos, many=True)
        
        return paginator.get_paginated_response(serializer.data)




class PagoDeUnAlumnoViewSet(APIView):
    pagination_class = PagoResultsSetPagination
    serializer_class = PagoDeUnAlumnoSerializer      

    def post(self, request, alumno_id, *args, **kwargs):

        pago_data = request.data  
        serializer = self.serializer_class(data=pago_data)  
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()  

    def get_success_headers(self, data):
        return {}

class CompromisoDePagoViewSet(viewsets.ModelViewSet):
    queryset = CompromisoDePago.objects.all()
    serializer_class = CompromisoDePagoSerializer
    pagination_class = CompDePagResultsSetPagination
    filter_backends = [OrderingFilter]
    ordering_fields = ['anio']
    ordering = ['anio']

        
    @parser_classes([MultiPartParser, FormParser])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


    @action(detail=True, methods=['get'], url_path='archivo')
    def retrieve_pdf(self, request, pk=None):
        try:
            compromiso = self.get_object()
            if compromiso.archivo_pdf:
                # Extrae el nombre del archivo sin la ruta
                filename = os.path.basename(compromiso.archivo_pdf.name)
                response = FileResponse(compromiso.archivo_pdf.open(), content_type='application/pdf')
                response['Content-Disposition'] = f'inline ; filename="{filename}"'
                return response
            else:
                return Response({"detail": "El compromiso no tiene un archivo PDF asociado."}, status=status.HTTP_404_NOT_FOUND)
        except CompromisoDePago.DoesNotExist:
            return Response({"detail": "Compromiso no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        




#Esta vista no es usada
class FirmaCompPagoAlumnoViewSets(viewsets.ModelViewSet):
    pagination_class = FirmasResultSetPagination


class AlumnosFirmaronUltimoCompromisoView(viewsets.ViewSet):
    pagination_class = FirmasResultSetPagination

    def list(self, request):
        ultimo_compromiso = CompromisoDePago.objects.order_by('-fecha_carga_comp_pdf').first()

        # Si no hay compromiso, devuelve una lista vacía
        if not ultimo_compromiso:
            return Response([], status=status.HTTP_200_OK)

        firmas_ultimo_compromiso = FirmaCompPagoAlumno.objects.filter(compromiso_de_pago=ultimo_compromiso)

        serializer = FirmaCompPagoAlumnoCompletoSerializer(firmas_ultimo_compromiso, many=True)
        data = serializer.data

        return Response(data)

class AlumnosNoFirmaronUltimoCompromisoView(viewsets.ViewSet):
    pagination_class = FirmasResultSetPagination

    def list(self, request):
        ultimo_compromiso = CompromisoDePago.objects.order_by('-fecha_carga_comp_pdf').first()

        # Si no hay compromiso, devuelve una lista vacía
        if not ultimo_compromiso:
            return Response([], status=status.HTTP_200_OK)
        
        alumnos_firmaron_ids = FirmaCompPagoAlumno.objects.filter(
            compromiso_de_pago=ultimo_compromiso
        ).values_list('alumno_id', flat=True)

        alumnos_no_firmaron = Alumno.objects.exclude(user__dni__in=alumnos_firmaron_ids)

        # Si no hay alumnos que no han firmado, también puedes devolver una lista vacía
        if not alumnos_no_firmaron.exists():
            return Response([], status=status.HTTP_200_OK)

        serializer = AlumnoSerializer(alumnos_no_firmaron, many=True)
        data = serializer.data

        return Response(data, status=status.HTTP_200_OK)


class FirmarCompromisoView(APIView):

    def post(self, request, alumno_id=None):
        ultimo_compromiso = CompromisoDePago.objects.order_by('-fecha_carga_comp_pdf').first()
        alumno= Alumno.objects.get(user=alumno_id)

        if ultimo_compromiso == None:
            return Response({"detail": "No payment commitments found"}, status=status.HTTP_404_NOT_FOUND)
        

        firma_ultimo_comp = FirmaCompPagoAlumno.objects.create(
        alumno=alumno,
        compromiso_de_pago=ultimo_compromiso
        )

        firma_ultimo_comp = FirmaCompPagoAlumno.objects.filter(alumno=alumno_id, compromiso_de_pago=ultimo_compromiso.id_comp_pago)    
        serializer = FirmaCompPagoAlumnoSerializer(firma_ultimo_comp, many=True)
        
        #Generar cuotas de manera automatica
        generar_cuotas(alumno_id,ultimo_compromiso)

        return Response(serializer.data)


class UltimoCompromisoDePagoViewSet(APIView):
    
    def get(self, request):
        ultimo_compromiso = CompromisoDePago.objects.order_by('-fecha_carga_comp_pdf').first()
        if ultimo_compromiso is not None:
            serializer = CompromisoDePagoSerializer(ultimo_compromiso, context={'request': request})
            return Response(serializer.data)
        return Response({"detail": "No data found."}, status=status.HTTP_404_NOT_FOUND) 
  


class FirmasDeUnAlumnoView(viewsets.ReadOnlyModelViewSet):
    pagination_class = FirmasResultSetPagination

    def list(self, request, alumno_id=None):
        firmas_comp_todas = FirmaCompPagoAlumno.objects.filter(alumno_id=alumno_id)
        ultimo_compromiso = CompromisoDePago.objects.order_by('-fecha_carga_comp_pdf').first()

        # Aplicar paginación
        page = self.paginate_queryset(firmas_comp_todas)
        if page is not None:
            serializer = FirmaCompPagoAlumnoSerializer(page, many=True)
            data = serializer.data
            for item in data:
                item['firmo_ultimo_compromiso'] = FirmaCompPagoAlumno.objects.filter(
                    alumno_id=alumno_id, 
                    compromiso_de_pago=ultimo_compromiso
                ).exists()
            return self.get_paginated_response(data)

        serializer = FirmaCompPagoAlumnoSerializer(firmas_comp_todas, many=True)
        data = serializer.data
        for item in data:
            item['firmo_ultimo_compromiso'] = FirmaCompPagoAlumno.objects.filter(
                alumno_id=alumno_id, 
                compromiso_de_pago=ultimo_compromiso
            ).exists()

        return Response(data)

class CuotaViewSet(viewsets.ModelViewSet):
    queryset: BaseManager[Cuota] = Cuota.objects.all()
    pagination_class = CuotasResultSetPagination
    lookup_field = 'alumno_id'
    serializer_class = CuotaSerializer

    def list(self, request, alumno_id=None):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)



class CuotaDeUnAlumnoViewSet(viewsets.ModelViewSet):
    lookup_field = 'alumno_id'
    queryset: BaseManager[Cuota] = Cuota.objects.all().order_by('id_cuota') 
    serializer_class = CuotaDeUnAlumnoSerializer
    pagination_class = CuotasResultSetPagination

   

    def list(self, request, alumno_id=None):
        queryset = self.get_queryset().filter(alumno_id=alumno_id)
        serializer = self.get_serializer(queryset, many=True)

        # Aplicar paginación
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CuotaDeUnAlumnoSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        return Response(serializer.data)


class CuotasImpagasDeUnAlumnoViewSet(viewsets.ModelViewSet):
    lookup_field = 'alumno_id'
    serializer_class = CuotaDeUnAlumnoSerializer
    pagination_class = CuotasResultSetPagination

    def get_queryset(self):
        alumno_id = self.kwargs.get('alumno_id')
        if not alumno_id:
            return Cuota.objects.none()
            
        return Cuota.objects.filter(
            alumno_id=alumno_id
        ).exclude(
            lineadepago__pago__estado="Confirmado" 
        ).distinct()

    def list(self, request, alumno_id=None):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class AlumnosConMatriculaPagadaViewSet(viewsets.ViewSet):
    """
    Vista para obtener los alumnos que han pagado completamente la matrícula.
    """
    def list(self, request):
        # Filtrar las cuotas que son del tipo "Matricula" y están en estado "Pagada completamente"
        cuotas_matricula_pagada = Cuota.objects.filter(tipo="Matricula", estado="Pagada Completamente")
        print("Pepe", cuotas_matricula_pagada)

        # Obtener los IDs de los alumnos asociados a estas cuotas
        alumnos_ids = cuotas_matricula_pagada.values_list('alumno_id', flat=True).distinct()

        # Filtrar los alumnos que tienen esas cuotas
        alumnos_con_matricula_pagada = Alumno.objects.filter(user_id__in=alumnos_ids)

        # Serializar los datos de los alumnos
        serializer = AlumnoSerializer(alumnos_con_matricula_pagada, many=True)

        # Retornar la respuesta con los datos serializados
        return Response(serializer.data, status=status.HTTP_200_OK)