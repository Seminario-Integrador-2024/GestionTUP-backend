from .email_config import enviar_email, configurar_mail
from ..alumnos.models import Alumno
from ..pagos.models import LineaDePago, Cuota
from django.db import models


def tomar_datos_del_pago(pago):


    from ..pagos.api.serializers import PagoDeUnAlumnoSerializer

    # Serializar el pago para obtener la información
    pago_serializer = PagoDeUnAlumnoSerializer(pago)
    datos_pago = pago_serializer.data

    # Preparar el correo
    alumno_buscar = datos_pago.get('alumno')
    alumno = Alumno.objects.get(user=alumno_buscar)     
    monto_informado = datos_pago.get('monto_informado')
    comentario = datos_pago.get('comentario', 'No hay comentario')
    cuotas_ids = [cuota.get('nro_cuota') for cuota in datos_pago.get('cuotas', [])]
    cuotas = Cuota.objects.filter(alumno=alumno,nro_cuota__in=cuotas_ids)

    # Extraer solo el número, estado y monto de cada cuota
    cuotas_info = []
    for cuota in datos_pago.get('cuotas', []):
        nro_cuota = cuota.get('nro_cuota')
        
        # Filtrar todas las líneas de pago que pertenecen a la cuota actual
        total_pagado_anteriormente = LineaDePago.objects.filter(cuota__in=cuotas).aggregate(total=models.Sum('monto_aplicado'))['total'] or 0.0
        
        cuota_info = {
            'nro_cuota': nro_cuota,
            'estado': cuota.get('estado'),
            'monto': cuota.get('monto'),
            'tipo': cuota.get('tipo'),
            'fecha_informado': cuota.get('fecha_informado'),
            'valorpagado': cuota.get('valorpagado'),
            'total_pagado_anteriormente': total_pagado_anteriormente  # Agregamos el total pagado previamente
        }
        
        cuotas_info.append(cuota_info)


    # Definir el asunto del correo
    subject = f"Confirmación de pago del alumno {alumno.user.full_name}"

    # Crear el cuerpo del mensaje
    body = f"""
    Estimado/a Tesorería,

    Hemos recibido el siguiente pago:

    Alumno:{alumno.user.full_name}
    DNI: {alumno.user.dni}
    Email:{alumno.user.email}
    Monto del pago informado: ${monto_informado}
    Comentario: {comentario}
    Nombre de la Carrera: Tecnicatura Universitaria en Programación
    Fecha: {cuota['fecha_informado']}
    Detalle de Cuotas:
    """
    
    for cuota in cuotas_info:
        if cuota['tipo'] == "Cuota":
            body += f"\n- Cuota {cuota['nro_cuota']} - Monto total de la cuota: $ {cuota['monto']} \n"
        else:
             body += f"\n- Matricula {cuota['nro_cuota']} - Monto total de la matricula: $ {cuota['monto']} \n"


    body += "\nPor favor, proceder con las verificaciones correspondientes.\n\nAtentamente,\nGestiónTUP de Pagos"
    
    return  {'subject': subject, 'body': body}



def enviar_mail_del_pago_a_tosoreria(pago):
    #Armar el contenido del mail
    contenido = tomar_datos_del_pago(pago)
    #Configurar el mansaje entero
    email = configurar_mail(contenido['body'], contenido['subject'])
    #Enviar el email
    enviar_email(email)


