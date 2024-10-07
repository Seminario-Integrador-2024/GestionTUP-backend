import os
from dotenv import load_dotenv
from email.message import EmailMessage 
import ssl
import smtplib
from pathlib import Path



dotenv_path = Path(__file__).resolve().parent.parent.parent / '.envs' / '.local' / '.email'
load_dotenv(dotenv_path)


class Credenciales:
    password = os.getenv("PASSWORD")
    email_sender = "gestiontup2024@gmail.com"
    email_reciver = "tesoreriautnpruebas2024@gmail.com"


def configurar_mail(body, subject, email_reciver = None):

    em = EmailMessage()
    em["From"] = Credenciales.email_sender
    em["To"] = email_reciver if email_reciver else Credenciales.email_reciver  
    em["Subject"] = subject
    em.set_content(body)

    return em

# Función para enviar el correo
def enviar_email(mensaje):
    em = mensaje
    # Crear contexto SSL
    context = ssl.create_default_context()
    
    # Enviar el correo
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(Credenciales.email_sender, Credenciales.password)  # Usar credenciales desde la clase
        smtp.sendmail(Credenciales.email_sender, Credenciales.email_reciver, em.as_string())


"""def configurar_mail(body,subject):
    # Configurar el correo
    em = EmailMessage()
    em["From"] = email_sender
    em["To"] = email_reciver
    em["Subject"] = subject
    em.set_content(body)

    return em

def enviar_email(mensaje):
    em = mensaje
    # Crear contexto SSL
    context = ssl.create_default_context()
    
    # Enviar el correo
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(email_sender, password)
        smtp.sendmail(email_sender, email_reciver, em.as_string())"""
