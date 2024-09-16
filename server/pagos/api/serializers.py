from rest_framework import serializers
from ..models import *
from django.urls import reverse

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



"""class CuotaSerializer(serializers.ModelSerializer):
    
    monto = serializers.SerializerMethodField()

    class Meta:
        model = Cuota
        fields = "__all__"
        
    def get_monto(self, obj):
        compromiso_de_pago = obj.compdepago
        if compromiso_de_pago:
            return compromiso_de_pago.monto_completo
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('compdepago', None)
        return representation"""

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



"""
lista de cuotas vendra en el body del post con este formato 
[
    {
        "cuotas": [1,2,3],
        "monto_informado": 1000,
        "ticket": "imagen.jpg"
    }
]
"""


class PagoSerializer(serializers.ModelSerializer):
    alumno_id = serializers.PrimaryKeyRelatedField(queryset=Alumno.objects.all())
    cuotas = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    monto_informado = serializers.FloatField(write_only=True)
    ticket = serializers.ImageField()

    class Meta:
        model = Pago
        fields = ['alumno_id', 'cuotas', 'monto_informado', 'ticket']

    def create(self, validated_data):
        cuotas_ids = validated_data.pop('cuotas')
        monto_informado = validated_data.pop('monto_informado')
        
        pago = Pago.objects.create(**validated_data)
        
        cuotas = Cuota.objects.filter(id_cuota__in=cuotas_ids)
        monto_restante = monto_informado
        
        for cuota in cuotas:
            monto_aplicado = min(cuota.monto, monto_restante)
            LineaDePago.objects.create(pago=pago, cuota=cuota, monto_aplicado=monto_aplicado)
            monto_restante -= monto_aplicado
            
            if monto_restante <= 0:
                break
        
        return pago
