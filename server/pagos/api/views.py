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

# third party imports
from .serializers import *
from ..paginations import *
#utils imports
from ..utils import generar_cuotas

class PagoViewSet(viewsets.ModelViewSet):
    queryset : BaseManager[Pago] = Pago.objects.all()
    serializer_class = PagoSerializer
    pagination_class = PagoResultsSetPagination


"""class PagoDeUnAlumnoViewSet(APIView):
    queryset = Pago.objects.all()
    pagination_class = PagoResultsSetPagination
    serializer_class = PagoSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
"""

class PagoDeUnAlumnoViewSet(APIView):
    pagination_class = PagoResultsSetPagination
    serializer_class = PagoDeUnAlumnoSerializer

    def get_queryset(self, alumno_id):
        return Pago.objects.filter(alumno_id=alumno_id)

    def post(self, request, alumno_id, *args, **kwargs):
        # Se espera una lista de pagos
        pagos_data = request.data  # Esto ya es una lista de diccionarios

        # Iterar sobre cada pago en la lista y asignarle el alumno_id
        for pago_data in pagos_data:
            pago_data['alumno_id'] = alumno_id

        # Validar cada pago utilizando el serializador
        serializer = self.get_serializer(data=pagos_data, many=True)
        serializer.is_valid(raise_exception=True)

        # Guardar los pagos en la base de datos
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    
class CompromisoDePagoViewSet(viewsets.ModelViewSet):
    queryset = CompromisoDePago.objects.all()
    serializer_class = CompromisoDePagoSerializer
    pagination_class = CompDePagResultsSetPagination
    filter_backends = [OrderingFilter]
    ordering_fields = ['anio']
    ordering = ['anio']

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

    """    
    lookup_field = "alumno_id"
    serializer_class = FirmaCompPagoAlumnoSerializer
    queryset = FirmaCompPagoAlumno.objects.all()

    def get_queryset(self):
        
        alumno_id = self.kwargs.get(self.lookup_field)

        ultimo_compromiso = CompromisoDePago.objects.order_by('-fecha_carga_comp_pdf').first()

        if not ultimo_compromiso:
            return FirmaCompPagoAlumno.objects.none()
        else:
            firma_ultimo_comp = FirmaCompPagoAlumno.objects.filter(
            alumno_id=alumno_id,
            compromiso_de_pago_id=ultimo_compromiso.id_comp_pago
            )
            if not firma_ultimo_comp.exists():
                return FirmaCompPagoAlumno.objects.none()
            else:
                #generar_cuotas(alumno_id,ultimo_compromiso)
                return firma_ultimo_comp
    """
            
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
  


"""    def retrieve(self, request, *args, **kwargs):
        ultimo_compromiso = CompromisoDePago.objects.order_by('-fecha_carga_comp_pdf').first()

        if not ultimo_compromiso:
            return Response({"detail": "No payment commitments found"}, status=status.HTTP_404_NOT_FOUND)

        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({"detail": "No student signatures were found."}, status=status.HTTP_404_NOT_FOUND)

        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)"""

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


    

    def list(self, request, alumno_id=None):
        queryset = self.get_queryset().filter(alumno_id=alumno_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
