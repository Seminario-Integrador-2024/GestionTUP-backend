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
    tipocuota = serializers.CharField(source='tipo')

    valorpagado = serializers.SerializerMethodField()
    valorinformado = serializers.SerializerMethodField()

    def get_valorinformado(self, instance):
        # Buscar el monto aplicado a esta cuota a través de LineaDePago
        linea_pagos = LineaDePago.objects.filter(cuota=instance)
        return sum(linea_pago.monto_aplicado for linea_pago in linea_pagos)
    
    def get_valorpagado(self, instance):
        # Sumar todos los montos aplicados a esta cuota a través de LineaDePago
        linea_pagos = LineaDePago.objects.filter(cuota=instance)
        return sum(linea_pago.monto_aplicado for linea_pago in linea_pagos)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation

    class Meta:
        model = Cuota
        fields = ['numero', 'montoActual', 'fechaVencimiento', 'valorpagado', 'estado', 'tipocuota', 'valorinformado']




class PagoSerializer(serializers.ModelSerializer):
     class Meta:
        model = Pago
        fields = "__all__"



class PagoDeUnAlumnoRetrieveSerializer(serializers.ModelSerializer):
    cuotas = serializers.SerializerMethodField() 

    class Meta:
        model = Pago
        fields = ['monto_informado', 'ticket', 'estado', 'fecha', 'cuotas','comentario']

    def get_cuotas(self, obj):
      
        lineas_pago = LineaDePago.objects.filter(pago=obj)
        cuotas = [linea.cuota for linea in lineas_pago] 
        return CuotaSerializer(cuotas, many=True).data 



class PagoDeUnAlumnoSerializer(serializers.ModelSerializer):
    cuotas = serializers.ListField(write_only=True)
    monto_informado = serializers.FloatField(write_only=True)
    ticket = serializers.ImageField()
    comentario = serializers.CharField(required = False, allow_blank=True)


    class Meta:
        model = Pago
        fields = ['alumno', 'cuotas', 'monto_informado', 'ticket', 'comentario']

    def create(self, validated_data):
        cuotas_ids_str = validated_data.pop('cuotas')
        cuotas_ids_str = ','.join(map(str, cuotas_ids_str))
        cuotas_ids = [int(id_str) for id_str in cuotas_ids_str.split(',')]

        monto_informado = validated_data.pop('monto_informado')
        alumno = validated_data.pop('alumno')
        comentario = validated_data.pop('comentario')
        print("____________________________",comentario,type(comentario))

        

        pago = Pago.objects.create(
            monto_informado=monto_informado,
            alumno=alumno,
            ticket=validated_data.get('ticket'),
            estado="Informado",
            comentario = comentario if comentario is not '' else "Informado desde GestiónTUP"
        )

        cuotas = Cuota.objects.filter(id_cuota__in=cuotas_ids)
        monto_restante = monto_informado

        for cuota in cuotas:
            if monto_restante <= 0:
                break

            # Obtener el total pagado previamente para esta cuota
            total_pagado_anteriormente = LineaDePago.objects.filter(cuota=cuota).aggregate(total=models.Sum('monto_aplicado'))['total'] or 0.0

            # Lógica para manejar los distintos casos de pago
            if cuota.estado in ['Impaga', 'Vencida']:
                # Pago completo a una cuota impaga
                if monto_restante >= (cuota.monto - total_pagado_anteriormente):
                    LineaDePago.objects.create(pago=pago, cuota=cuota, monto_aplicado=cuota.monto - total_pagado_anteriormente)
                    cuota.estado = 'Pagada completamente'
                    cuota.fecha_informado = timezone.now()
                    monto_restante -= (cuota.monto - total_pagado_anteriormente)
                else:
                    LineaDePago.objects.create(pago=pago, cuota=cuota, monto_aplicado=monto_restante)
                    cuota.estado = 'Pagada parcialmente'
                    cuota.fecha_informado = timezone.now()
                    monto_restante = 0
            elif cuota.estado == 'Pagada parcialmente':
                # Caso de pago parcial sobre cuota que ya fue parcialmente pagada
                if monto_restante > 0:
                    monto_aplicado = min(cuota.monto - total_pagado_anteriormente, monto_restante)
                    LineaDePago.objects.create(pago=pago, cuota=cuota, monto_aplicado=monto_aplicado)
                    total_pagado_actual = total_pagado_anteriormente + monto_aplicado

                    if total_pagado_actual >= cuota.monto:
                        cuota.estado = 'Pagada completamente'
                        cuota.fecha_informado = timezone.now()

                    monto_restante -= monto_aplicado

            cuota.save()

        return pago
