
import os
from dotenv import load_dotenv
from email.message import EmailMessage 
import ssl
import smtplib

load_dotenv()

password = os.getenv("PASSWORD")
email_sender = "gestiontup2024@gmail.com"
email_reciver = "ulisespallares8@gmail.com"

em = EmailMessage()

subject = "Asunto del mensaje"
body = "Este es un mensaje"

em["From"] = email_sender
em["To"] = email_reciver
em["subject"] = subject
em.set_content(body)

context = ssl.create_default_context()

with smtplib.SMTP_SSL("smtp.gmail.com",465,context=context) as smtp:
    smtp.login(email_sender,password)
    smtp.sendmail(email_sender,email_reciver,em.as_string())