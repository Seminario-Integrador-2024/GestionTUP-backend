# python imports 
import datetime
import environ
import django
from django.utils import timezone
import os
import dj_database_url
# Cargar el archivo .env
env = environ.Env()
environ.Env.read_env(os.path.join(os.path.dirname(__file__), "../.postgres"))

# Configuración de la base de datos
DATABASES = {
    'default': env.db(),  # Usa environ para configurar la base de datos
}



DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(default=DATABASE_URL)
    }


# Configuración de Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()


# Mis imports
from server.pagos.models import Cuota, CompromisoDePago, LineaDePago, FirmaCompPagoAlumno
from server.alumnos.models import Alumno, Inhabilitacion
from server.materias.models import Materia, MateriaAlumno
from server.emails_controller.email_config import configurar_mail, enviar_email, Credenciales


def aviso_de_vencimiento_dos_dias():
    hoy = timezone.now().date()
    dos_dias_despues = hoy + datetime.timedelta(days=2)
    
    ultimo_compromiso = CompromisoDePago.objects.order_by('-fecha_carga_comp_pdf').first()
    if not ultimo_compromiso:
        print("No hay compromisos de pago.")
        return

    fechas_vencimiento = [
        ultimo_compromiso.fecha_vencimiento_1,
        ultimo_compromiso.fecha_vencimiento_2,
        ultimo_compromiso.fecha_vencimiento_3
    ]

    if dos_dias_despues.day in fechas_vencimiento:
        
        alumnos_activos = Alumno.objects.filter(estado_academico="Activo")
        for alumno in alumnos_activos:
            cuotas_por_vencer = Cuota.objects.filter(
                alumno=alumno,
                fecha_vencimiento=dos_dias_despues,
                estado__in=["Impaga", "Vencida", "Pagada parcialmente"]
            )
            
            if cuotas_por_vencer.exists():
                enviar_email_de_aviso_de_vencimiento(alumno, cuotas_por_vencer, dos_dias_despues)

def enviar_email_de_aviso_de_vencimiento(alumno, cuotas, fecha_vencimiento):

    print(f"{datetime.datetime.now()} - Tarea programada: Envio de email por proximo vencimiento ")

    subject = "Aviso de vencimiento de cuotas"
    body = f"Estimado/a {alumno.user.full_name},\n\n"
    body += f"Le recordamos que el día {fecha_vencimiento.strftime('%d/%m/%Y')} vencen las siguientes cuotas:\n\n"
    
    for cuota in cuotas:
        body += f"- {cuota.tipo} {cuota.nro_cuota}: Monto ${cuota.monto}\n"

    body += "\nPor favor, asegúrese de realizar el pago antes de la fecha de vencimiento para evitar recargos.\n"
    body += "Si ya ha realizado el pago, por favor ignore este mensaje.\n\n"
    body += "Saludos cordiales,\nTesorería UTN"

   
    email_recipient = "tesoreriautnpruebas2024@gmail.com"  
    mensaje = configurar_mail(body, subject, email_recipient)
    try:
        enviar_email(mensaje)
        print(f"Correo de aviso enviado a: {email_recipient}")
    except Exception as e:
        print(f"Error al enviar correo de aviso a {email_recipient}: {e}")

#--------------------------------------------------------------------------------------------

def actualizacion_de_cuotas():
    alumnos_activos = Alumno.objects.filter(estado_academico="Activo")

    ultimo_compromiso = CompromisoDePago.objects.order_by('-fecha_carga_comp_pdf').first()
    
    fechas_vencimiento_1_2_3 = [ultimo_compromiso.fecha_vencimiento_1,
                                ultimo_compromiso.fecha_vencimiento_2,
                                ultimo_compromiso.fecha_vencimiento_3]
    
    hoy = timezone.now().date()
    
    if not ultimo_compromiso:
        print("No hay compromisos de pago.")
        return {}

    alumnos_cuota_vencida = {}

    if hoy.day in fechas_vencimiento_1_2_3:
        print(f"{datetime.datetime.now()} - Tarea programada: Actualización de cuotas ")
        
        anio_actual = hoy.year
       
        cant_max_materias = 2

        if hoy.month < 3 or hoy.month > 12:
            print("Fuera de rango para actualización.")
            return {}


        for alumno in alumnos_activos:
            cant_materias_alumno = MateriaAlumno.objects.filter(id_alumno=alumno.user.dni, anio=anio_actual).count()
            cuotas_pendientes = Cuota.objects.filter(
                fecha_vencimiento__lte=hoy,
                alumno=alumno,
                estado__in=["Impaga", "Vencida", "Pagada parcialmente"],
            )
            
                
            if cuotas_pendientes.exists():       

                fechas_vencimiento_monto = {}

                if cant_materias_alumno > cant_max_materias:
                    if hoy.day >= ultimo_compromiso.fecha_vencimiento_1 and hoy.day < ultimo_compromiso.fecha_vencimiento_2:
                        fechas_vencimiento_monto[ultimo_compromiso.fecha_vencimiento_2] = ultimo_compromiso.monto_completo_2venc
                    elif hoy.day >= ultimo_compromiso.fecha_vencimiento_2:
                        fechas_vencimiento_monto[ultimo_compromiso.fecha_vencimiento_3] = ultimo_compromiso.monto_completo_3venc
                else:
                    if hoy.day >= ultimo_compromiso.fecha_vencimiento_1 and hoy.day < ultimo_compromiso.fecha_vencimiento_2:
                        fechas_vencimiento_monto[ultimo_compromiso.fecha_vencimiento_2] = ultimo_compromiso.monto_reducido__2venc
                    elif hoy.day >= ultimo_compromiso.fecha_vencimiento_2:
                        fechas_vencimiento_monto[ultimo_compromiso.fecha_vencimiento_3] = ultimo_compromiso.monto_reducido_3venc
            
            for cuota in cuotas_pendientes:

                if cuota.fecha_vencimiento.month < hoy.month:
                    alumno.estado_financiero = "Inhabilitado" 
                    alumno.save()

                    descripcion = f"El alumno {alumno.user.full_name} ha sido inhabilitado por falta de pagos"
                    
                    tiene_inhabilitacion = Inhabilitacion.objects.filter(id_alumno = alumno, fecha_hasta__isnull = True).exists()

                    if not tiene_inhabilitacion:

                        Inhabilitacion.objects.create(
                            id_alumno=alumno,
                            fecha_desde=timezone.make_aware(datetime.datetime.combine(hoy, datetime.time.min)),
                            descripcion=descripcion
                        )

                else:    
                    cuota.fecha_vencimiento = datetime.date(hoy.year, hoy.month, list(fechas_vencimiento_monto.keys())[0])
                    
                    if cuota.estado in ["Impaga", "Vencida"]:
                        cuota.estado = "Vencida"
                    
                    if cuota.tipo != "Matrícula":
                        cuota.monto = list(fechas_vencimiento_monto.values())[0]
                    
                    cuota.save()

                
                if alumno in alumnos_cuota_vencida:
                    alumnos_cuota_vencida[alumno].append(cuota)
                else:
                    alumnos_cuota_vencida[alumno] = [cuota]
        else:
            return {}

    return alumnos_cuota_vencida


def enviar_aviso_de_vencimiento(alumnos_cuota_vencida):


    if not alumnos_cuota_vencida:
        print("No hay correos que enviar.")
        return

    print(f"{datetime.datetime.now()} - Tarea programada: Envio de email por actualización de cuotas ")
    

    for alumno, cuotas_actualizadas in alumnos_cuota_vencida.items():
        subject = "Actualización de cuotas"
        body = f"Estimado/a {alumno.user.full_name},\n\n"
        body += "Se han actualizado los montos y las fechas de vencimiento de las siguientes cuotas:\n\n"
        
        for cuota in cuotas_actualizadas:
            if cuota.tipo =="Cuota":
                body += f"- Cuota {cuota.nro_cuota}: Nuevo monto ${cuota.monto}, vence el {cuota.fecha_vencimiento}\n"
            else:
                body += f"- Cuota {cuota.nro_cuota} (Matrícula): Monto ${cuota.monto}, vence el {cuota.fecha_vencimiento}\n"

        body += "\nNo te olvides de abonar antes de las fechas de vencimiento.\n"
        body += "Saludos.\nAtte. Tesorería"
        

        email_recipient = "tesoreriautnpruebas2024@gmail.com"  

        mensaje = configurar_mail(body, subject, email_recipient)
        try:
            enviar_email(mensaje)
            print(f"Correo enviado a: {email_recipient}")
        except Exception as e:
            print(f"Error al enviar correo a {email_recipient}: {e}")

    print("Correos enviados")


if __name__ == "__main__":
    alumnos_cuota_vencida = actualizacion_de_cuotas()
    #enviar_aviso_de_vencimiento(alumnos_cuota_vencida)
    #aviso_de_vencimiento_dos_dias()
    print("Cuotas actualizadas")

    print("Contenido de alumnos_cuota_vencida:")
    for alumno, cuotas in alumnos_cuota_vencida.items():
        print(f"\nAlumno: {alumno} {alumno.estado_financiero}")
        print("Cuotas vencidas:")
        for cuota in cuotas:
            print(f"  - Nro. Cuota: {cuota.nro_cuota}")
            print(f"    Fecha de vencimiento: {cuota.fecha_vencimiento}")
            print(f"    Monto: {cuota.monto}")
            print(f"    Estado: {cuota.estado}")
