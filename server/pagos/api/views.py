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

# third party imports
from .serializers import *
from ..paginations import *
#utils imports
from ..utils.utils import generar_cuotas

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

    @parser_classes([MultiPartParser, FormParser])
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

    """    
    @parser_classes([MultiPartParser, FormParser])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    """


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
    queryset = FirmaCompPagoAlumno.objects.all()
    serializer_class = FirmaCompPagoAlumnoSerializer
    pagination_class = FirmasResultSetPagination


            
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
  


class FirmasDeUnAlumnoView(viewsets.ViewSet):

    pagination_class = FirmasResultSetPagination

    def list(self, request, alumno_id=None):
        firmas_comp_todas = FirmaCompPagoAlumno.objects.filter(alumno_id=alumno_id)
        ultimo_compromiso = CompromisoDePago.objects.order_by('-fecha_carga_comp_pdf').first()
        
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
    queryset: BaseManager[Cuota] = Cuota.objects.all()
    serializer_class = CuotaDeUnAlumnoSerializer
    pagination_class = PagoResultsSetPagination
    

    def list(self, request, alumno_id=None):
        queryset = self.get_queryset().filter(alumno_id=alumno_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
