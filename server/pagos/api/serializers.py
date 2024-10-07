from rest_framework import serializers
from rest_framework import status
from ..models import *
from django.urls import reverse
from django.utils import timezone
from rest_framework.response import Response
from ...materias.models import Materia, MateriaAlumno
from ...alumnos.models import Alumno
from ...emails_controller.email_sender_pagos import enviar_mail_del_pago_a_tosoreria

# Create your serializers here.

class CompromisoDePagoSerializer(serializers.ModelSerializer):
    fecha_vencimiento_1 = serializers.IntegerField(required=False)
    fecha_vencimiento_2 = serializers.IntegerField(required=False)
    fecha_vencimiento_3 = serializers.IntegerField(required=False)

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
    compromiso_de_pago = serializers.SerializerMethodField()  # Usar SerializerMethodField

    class Meta:
        model = Cuota
        exclude = ['compdepago']  # Incluir todos los campos del modelo

    def get_compromiso_de_pago(self, obj):
        compromiso = obj.compdepago  # Asegúrate de que 'compdepag' sea el campo correcto

        if compromiso:
            anio = compromiso.anio.year % 100  # Obtener los últimos 2 dígitos del año
            cuatrimestre = str(compromiso.cuatrimestre).zfill(2)  # Asegurarse de que tenga 2 dígitos
            
            return f"{cuatrimestre}/{anio:02}"  # Retornar el formato deseado
        return None  # Retornar None si no hay compromiso

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()  # Obtener el queryset
        serializer = self.get_serializer(queryset, many=True)  # Serializar el queryset
        return Response(serializer.data)  # Retornar la respuesta
    



class FirmaCompPagoAlumnoSerializer(serializers.ModelSerializer):
    compromiso_de_pago = serializers.SerializerMethodField()
    id_compromiso_de_pago = serializers.SerializerMethodField()


    class Meta:
        model = FirmaCompPagoAlumno
        fields = "__all__"

    def get_id_compromiso_de_pago(self, obj):
        compromiso = obj.compromiso_de_pago
        return compromiso.id_comp_pago

    def get_compromiso_de_pago(self, obj):
        compromiso = obj.compromiso_de_pago
        
        if compromiso:
            anio = compromiso.anio.year % 100 
            cuatrimestre = str(compromiso.cuatrimestre).zfill(2)  
            
            return f"{cuatrimestre}/{anio:02}" 
        return None

class FirmaCompPagoAlumnoCompletoSerializer(serializers.ModelSerializer):
    compromiso_de_pago = serializers.SerializerMethodField()

    dni = serializers.IntegerField(source="alumno.user.dni", read_only=True)
    email = serializers.EmailField(source="alumno.user.email", read_only=True)
    full_name = serializers.CharField(source="alumno.user.full_name", read_only=True)
    legajo = serializers.CharField(source="alumno.legajo", read_only=True)

    class Meta:
        model = FirmaCompPagoAlumno
        fields = [
            "id",
            "dni", 
            "email", 
            "full_name", 
            "legajo",
            "firmado",
            "compromiso_de_pago",
            "fecha_firmado",
        ]

    def get_compromiso_de_pago(self, obj):
        compromiso = obj.compromiso_de_pago
        
        if compromiso:
            anio = compromiso.anio.year % 100 
            cuatrimestre = str(compromiso.cuatrimestre).zfill(2)  
            
            return f"{cuatrimestre}/{anio:02}" 
        return None
    
class AlumnoSerializer(serializers.ModelSerializer):
    dni = serializers.IntegerField(source="user.dni", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    class Meta:
        model = Alumno
        fields = [
            "dni", 
            "email", 
            "full_name", 
            "legajo", 
            "estado", 
            "anio_ingreso", 
            "telefono", 
            "tel_res", 
            "celular", 
            "gender"
        ]

class CuotaDeUnAlumnoSerializer(serializers.ModelSerializer):
    numero = serializers.IntegerField(source='nro_cuota')
    montoActual = serializers.FloatField(source='monto')
    fechaVencimiento = serializers.DateField(source='fecha_vencimiento')
    tipocuota = serializers.CharField(source='tipo')
    valorpagado = serializers.SerializerMethodField()
    valorinformado = serializers.SerializerMethodField()
    cuota_completa = serializers.SerializerMethodField()

    class Meta:
        model = Cuota
        fields = ['id_cuota','numero', 'montoActual', 'fechaVencimiento', 'valorpagado', 'estado', 'tipocuota', 'valorinformado','cuota_completa']

    def get_cuota_completa(self,instance):
        alumno = Alumno.objects.get(user=instance.alumno)
        anio_actual = timezone.now().year
        cant_materias_alumno = MateriaAlumno.objects.filter(id_alumno_id=instance.alumno,anio=anio_actual).count()
        if cant_materias_alumno > 2:
            return True
        else: 
            return False

    def get_valorinformado(self, instance):
        # Buscar el monto aplicado a esta cuota a través de LineaDePago
        linea_pagos = LineaDePago.objects.filter(cuota=instance)
        return sum(linea_pago.monto_aplicado for linea_pago in linea_pagos)
    
    def get_valorpagado(self, instance):    
        # Obtener todos los LineaDePago asociados a esta cuota
        linea_pagos = LineaDePago.objects.filter(cuota=instance)
        
        # Obtener todos los pagos correspondientes a estas líneas de pago
        pagos = Pago.objects.filter(id_pago__in=[linea_pago.pago.id_pago for linea_pago in linea_pagos])
        
        #Verificar estado de todos los pagos correspondientes a una cuota
        confirmado = True
        for pago in pagos:
            if pago.estado != "Confirmado":
                confirmado = False
        
        # Sumar el monto aplicado por cuota
        total_pagado_por_cuota = sum(linea_pago.monto_aplicado for linea_pago in linea_pagos)
        
        if confirmado:
            return total_pagado_por_cuota
        else:
            return 0

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation



class PagoSerializer(serializers.ModelSerializer):
     class Meta:
        model = Pago
        fields = "__all__"



class PagoDeUnAlumnoRetrieveSerializer(serializers.ModelSerializer):
    cuotas = serializers.SerializerMethodField() 

    class Meta:
        model = Pago
        fields = ['monto_informado', 'estado', 'fecha', 'cuotas','comentario']

    def get_cuotas(self, obj):
      
        lineas_pago = LineaDePago.objects.filter(pago=obj)
        cuotas = [linea.cuota for linea in lineas_pago] 
        return CuotaSerializer(cuotas, many=True).data 
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['fecha'] = instance.fecha.strftime('%Y-%m-%d') 
        return representation



class PagoDeUnAlumnoSerializer(serializers.ModelSerializer):
    cuotas = serializers.ListField(write_only=True)
    monto_informado = serializers.FloatField()
    comentario = serializers.CharField(required = False, allow_blank=True)


    class Meta:
        model = Pago
        fields = ['alumno', 'cuotas', 'monto_informado', 'comentario']

    
    def get_cuotas(self, obj):
        lineas_pago = LineaDePago.objects.filter(pago=obj)
        cuotas = [linea.cuota for linea in lineas_pago] 
        return CuotaSerializer(cuotas, many=True).data 

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['cuotas'] = self.get_cuotas(instance)
        return representation




    def create(self, validated_data):
        cuotas_ids_str = validated_data.pop('cuotas')
        cuotas_ids_str = ','.join(map(str, cuotas_ids_str))
        cuotas_ids = [int(id_str) for id_str in cuotas_ids_str.split(',')]

        monto_informado = float(validated_data.pop('monto_informado'))
        alumno = validated_data.pop('alumno')
        comentario = validated_data.pop('comentario')
        

        pago = Pago.objects.create(
            monto_informado=monto_informado,
            alumno=alumno,
            estado="Informado",
            comentario = comentario if comentario != '' else 'No hay comentarios',
        )     

        cuotas = Cuota.objects.filter(alumno=alumno,id_cuota__in=cuotas_ids)
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
                    LineaDePago.objects.create(pago=pago, cuota=cuota, monto_aplicado = cuota.monto - total_pagado_anteriormente)
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

        #Mandar el email a tesoeria
        enviar_mail_del_pago_a_tosoreria(pago)

        return pago
