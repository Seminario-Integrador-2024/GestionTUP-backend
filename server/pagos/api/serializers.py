from rest_framework import serializers
from rest_framework import status
from ..models import *
from django.urls import reverse
from django.utils import timezone
from rest_framework.response import Response

# Create your serializers here.

class CompromisoDePagoSerializer(serializers.ModelSerializer):
    archivo_pdf = serializers.FileField(write_only=True, required=False)
    archivo_pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = CompromisoDePago
        exclude = ['comprimiso_path']

    def get_archivo_pdf_url(self, obj):
        request = self.context.get('request')
        if obj.archivo_pdf:
            # Genera la URL completa al archivo PDF
            url = reverse('api:retrieve_pdf', args=[obj.pk])
            if request is not None:
                return request.build_absolute_uri(url)
            else:
                return url
        return None



class CuotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuota
        fields = "__all__"
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class FirmaCompPagoAlumnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FirmaCompPagoAlumno
        fields = "__all__"


class CuotaDeUnAlumnoSerializer(serializers.ModelSerializer):
    numero = serializers.IntegerField(source='nro_cuota')
    montoActual = serializers.FloatField(source='monto')
    fechaVencimiento = serializers.DateField(source='fecha_vencimiento')
    valorpagado = serializers.FloatField(source='monto')
    estado = serializers.CharField()
    tipo_cuota = serializers.CharField(source='tipo')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Puedes modificar los datos aquí si es necesario
        return representation

    class Meta:
        model = Cuota
        fields = ['numero', 'montoActual', 'fechaVencimiento', 'valorpagado', 'estado', 'tipo_cuota']




class PagoSerializer(serializers.ModelSerializer):
     class Meta:
        model = Pago
        fields = "__all__"


class PagoDeUnAlumnoSerializer(serializers.ModelSerializer):
    cuotas = serializers.ListField( write_only=True)
    monto_informado = serializers.FloatField(write_only=True)
    ticket = serializers.ImageField()
    

    class Meta:
        model = Pago
        fields = ['alumno', 'cuotas', 'monto_informado', 'ticket']

    def create(self, validated_data):
        cuotas_ids_str = validated_data.pop('cuotas')
        cuotas_ids_str = ','.join(map(str, cuotas_ids_str))
        cuotas_ids = [int(id_str) for id_str in cuotas_ids_str.split(',')]

        monto_informado = validated_data.pop('monto_informado')
        alumno = validated_data.pop('alumno')
        # El alumno_id será asignado desde la vista
     
        pago = Pago.objects.create(
        monto_informado=monto_informado,  # Asegúrate de asignar el monto informado
        alumno=alumno,
        ticket=validated_data.get('ticket'),
        estado = "Informado"
    )

        cuotas = Cuota.objects.filter(id_cuota__in=cuotas_ids)
        is_una_sola_cuota = len(cuotas) == 1 
        monto_restante = monto_informado

        for cuota in cuotas:
            if monto_restante <= 0:
                break

            # Lógica para manejar los distintos casos de pago
            if cuota.estado == 'Impaga':
                # Pago completo a una cuota impaga
                if monto_restante >= cuota.monto:
                    LineaDePago.objects.create(pago=pago, cuota=cuota, monto_aplicado=cuota.monto)
                    cuota.estado = 'Pagada completa'
                    cuota.fecha_informado = timezone.now()
                    monto_restante -= cuota.monto
                else:
                    LineaDePago.objects.create(pago=pago, cuota=cuota, monto_aplicado=monto_restante)
                    cuota.estado = 'Pagada parcialmente'
                    cuota.fecha_informado = timezone.now()
                    monto_restante = 0
            elif cuota.estado == 'Pagada parcialmente':
                # Caso de pago parcial sobre cuota que ya fue parcialmente pagada
                if monto_restante > 0:
                    monto_aplicado = min(cuota.monto - cuota.monto, monto_restante)
                    LineaDePago.objects.create(pago=pago, cuota=cuota, monto_aplicado=monto_aplicado)
                    cuota.monto += monto_aplicado
                    if cuota.monto >= cuota.monto:
                        cuota.estado = 'Pagada completa'
                        cuota.fecha_informado = timezone.now()
                    monto_restante -= monto_aplicado

            cuota.save()  # Guardar los cambios en el estado de la cuota

        return pago


