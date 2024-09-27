import os
from dotenv import load_dotenv
from email.message import EmailMessage 
import ssl
import smtplib
from pathlib import Path
from django.db import models
from ...alumnos.models import Alumno
from ..models import LineaDePago, Cuota

dotenv_path = Path(__file__).resolve().parent.parent.parent.parent / '.envs' / '.local' / '.email'
load_dotenv(dotenv_path)

password = os.getenv("PASSWORD")
email_sender = "gestiontup2024@gmail.com"
email_reciver = "tesoreriautnpruebas2024@gmail.com"


def enviar_email_de_pagos(pago):

    from ..api.serializers import PagoDeUnAlumnoSerializer

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

    print("#################################",cuotas_info)
    # Definir el asunto del correo
    subject = f"Confirmación de pago del alumno {alumno.user.full_name}"

    # Crear el cuerpo del mensaje
    body = f"""
    Estimado/a Tesorería,

    Hemos recibido el siguiente pago:

    Alumno:{alumno.user.full_name}
    DNI: {alumno.user.dni}
    Email:{alumno.user.email}
    CUIL: NN-DDDDDDD-N
    Monto del pago informado: ${monto_informado}
    Comentario: {comentario}
    Nombre de la Carrera: Tecnicatura Universitaria en Programación
    Fecha: {cuota['fecha_informado']}
    Detalle de Cuotas:
    """
    
    for cuota in cuotas_info:
        if cuota['tipo'] == "Cuota":
            body += f"\n- Cuota {cuota['nro_cuota']}: {cuota['estado']} - Monto total de la cuota: $ {cuota['monto']} - Suma de todos los pagos parciales: ${cuota['total_pagado_anteriormente']}\n"
        else:
             body += f"\n- Matricula {cuota['nro_cuota']}: {cuota['estado']} - Monto total de la matricula: $ {cuota['monto']} - Suma de todos los pagos parciales: ${cuota['total_pagado_anteriormente']}\n"


    body += "\nPor favor, proceder con las verificaciones correspondientes.\n\nAtentamente,\nGestiónTUP de Pagos"


    # Configurar el correo
    em = EmailMessage()
    em["From"] = email_sender
    em["To"] = email_reciver
    em["Subject"] = subject
    em.set_content(body)

    # Crear contexto SSL
    context = ssl.create_default_context()

    # Enviar el correo
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(email_sender, password)
        smtp.sendmail(email_sender, email_reciver, em.as_string())

    print(f"Correo enviado a {email_reciver} sobre el pago del alumno {alumno}.")

