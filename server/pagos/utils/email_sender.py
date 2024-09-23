import os
from dotenv import load_dotenv
from email.message import EmailMessage 
import ssl
import smtplib
from pathlib import Path

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
    alumno = datos_pago.get('alumno')
    monto = datos_pago.get('monto_informado')
    comentario = datos_pago.get('comentario', 'No hay comentario')
    nro_transferencia = datos_pago.get('nro_transferencia')

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
    subject = f"Confirmación de pago del alumno {alumno}"

    # Crear el cuerpo del mensaje
    body = f"""
    Estimado/a Tesorería,

    Hemos recibido el siguiente pago:

    Alumno: {alumno}
    Monto Total: {monto}
    Comentario: {comentario}
    Número de Transferencia: {nro_transferencia}

    Detalle de Cuotas:
    """
    
    for cuota in cuotas_info:
        body += f"\n- Cuota {cuota['nro_cuota']}: {cuota['estado']} - Monto: {cuota['monto']}\n"

    body += "\nPor favor, proceder con las verificaciones correspondientes.\n\nAtentamente,\nGestión de Pagos"

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


"""
import os
from dotenv import load_dotenv
from email.message import EmailMessage 
import ssl
import smtplib
from pathlib import Path

dotenv_path = Path(__file__).resolve().parent.parent.parent.parent / '.envs' / '.local' / '.email'
load_dotenv(dotenv_path)

password = os.getenv("PASSWORD")
email_sender = "gestiontup2024@gmail.com"
email_reciver = "tesoreriautnpruebas2024@gmail.com"

def enviar_email_de_pagos(pago):
        
    em = EmailMessage()

    subject = "Asunto del mensaje"
    
    
    

    em["From"] = email_sender
    em["To"] = email_reciver
    em["subject"] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com",465,context=context) as smtp:
        smtp.login(email_sender,password)
        smtp.sendmail(email_sender,email_reciver,em.as_string())"""