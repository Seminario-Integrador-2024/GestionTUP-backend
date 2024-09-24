import os
from dotenv import load_dotenv
from email.message import EmailMessage 
import ssl
import smtplib
from pathlib import Path

from ...alumnos.models import Alumno

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
    

    monto = datos_pago.get('monto_informado')
    comentario = datos_pago.get('comentario', 'No hay comentario')
    nro_transferencia = datos_pago.get('nro_transferencia')

    imagen_path = "http://localhost:8000"+datos_pago.get("ticket")

    # Extraer solo el número, estado y monto de cada cuota
    cuotas_info = []
    for cuota in datos_pago.get('cuotas', []):
        cuota_info = {
            'nro_cuota': cuota.get('nro_cuota'),
            'estado': cuota.get('estado'),
            'monto': cuota.get('monto')
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
    CUIL: NN-DDDDDDD-N
    Monto Total: {monto}
    Comentario: {comentario}
    Número de Transferencia: {nro_transferencia}
    Ticket: {imagen_path}

    Detalle de Cuotas:
    """
    
    for cuota in cuotas_info:
        body += f"\n- Cuota {cuota['nro_cuota']}: {cuota['estado']} - Monto: {cuota['monto']}\n"

    body += "\nPor favor, proceder con las verificaciones correspondientes.\n\nAtentamente,\nGestión de Pagos"

# Adjuntar la imagen si existe
    if imagen_path and os.path.exists(imagen_path):
        mime_type, _ = mimetypes.guess_type(imagen_path)
        if mime_type:
            maintype, subtype = mime_type.split('/')
            print(f"Adjuntando imagen: {imagen_path} con tipo MIME: {mime_type}")
            
            with open(imagen_path, 'rb') as img:
                em.add_attachment(img.read(), maintype=maintype, subtype=subtype, filename=os.path.basename(imagen_path))
        else:
            print(f"No se pudo determinar el tipo MIME para: {imagen_path}")
    else:
        print(f"La imagen no existe o la ruta no es válida: {imagen_path}")

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

