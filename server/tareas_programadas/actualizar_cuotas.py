# python imports 
import datetime
import environ
import django
from django.utils import timezone
import os

# Cargar el archivo .env
env = environ.Env()
environ.Env.read_env(os.path.join(os.path.dirname(__file__), "../.postgres"))

# Configuración de la base de datos
DATABASES = {
    'default': env.db(),  # Usa environ para configurar la base de datos
}


import os
import dj_database_url

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(default=DATABASE_URL)
    }


# Configuración de Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

#Verificación
print(f"{datetime.datetime.now()} - Tareas programadas ejecutándose")


# Mis imports
from server.pagos.models import Cuota, CompromisoDePago, LineaDePago, FirmaCompPagoAlumno
from server.alumnos.models import Alumno
from server.materias.models import Materia, MateriaAlumno
from server.emails_controller.email_config import configurar_mail, enviar_email, Credenciales



def actualizacion_de_cuotas():
    alumnos_activos = Alumno.objects.filter(estado_academico="Activo")

    ultimo_compromiso = CompromisoDePago.objects.order_by('-fecha_carga_comp_pdf').first()
    
    hoy = timezone.now().date()

    if not ultimo_compromiso:
        print("No hay compromisos de pago.")
        return {}

    if hoy.day > ultimo_compromiso.fecha_vencimiento_1:
        #alumnos_firm_ult_compdepag = FirmaCompPagoAlumno.objects.filter(compromiso_de_pago=ultimo_compromiso, alumno__in=alumnos_activos)
        
        anio_actual = hoy.year
        alumnos_cuota_vencida = {}
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
            ).order_by("nro_cuota")


            
                
            if cuotas_pendientes.exists():       

                fechas_vencimiento_monto = {}

                if cant_materias_alumno > cant_max_materias:
                    if hoy.day >= ultimo_compromiso.fecha_vencimiento_2:
                        fechas_vencimiento_monto[ultimo_compromiso.fecha_vencimiento_2] = ultimo_compromiso.monto_completo_2venc
                    elif hoy.day >= ultimo_compromiso.fecha_vencimiento_3:
                        fechas_vencimiento_monto[ultimo_compromiso.fecha_vencimiento_3] = ultimo_compromiso.monto_completo_3venc
                else:
                    if hoy.day >= ultimo_compromiso.fecha_vencimiento_2:
                        fechas_vencimiento_monto[ultimo_compromiso.fecha_vencimiento_2] = ultimo_compromiso.monto_reducido__2venc
                    elif hoy.day >= ultimo_compromiso.fecha_vencimiento_3:
                        fechas_vencimiento_monto[ultimo_compromiso.fecha_vencimiento_3] = ultimo_compromiso.monto_reducido_3venc
            
            for cuota in cuotas_pendientes:
                if cuota.estado in ["Impaga", "Vencida"]:
                    cuota.estado = "Vencida"
                    cuota.fecha_vencimiento = datetime.date(hoy.year, hoy.month, list(fechas_vencimiento_monto.keys())[0])
                    if cuota.tipo != "Matrícula":
                        cuota.monto = list(fechas_vencimiento_monto.values())[0]
                    cuota.save()


                if cuota.fecha_vencimiento.month < hoy.month:
                    alumno.estado_financiero = "Inhabilitado" 
                    ###############################
                    # Agregar a la tabla Inabilitaciones
                    ###############################
                
                if alumno in alumnos_cuota_vencida:
                    alumnos_cuota_vencida[alumno].append(cuota)
                else:
                    alumnos_cuota_vencida[alumno] = [cuota]

    return alumnos_cuota_vencida


def enviar_aviso_de_vencimiento(alumnos_cuota_vencida):
    if not alumnos_cuota_vencida:
        print("No hay correos que enviar.")
        return

    for alumno, cuotas in alumnos_cuota_vencida.items():
        body = f"Hola {alumno.user.full_name}, "
        subject = ""

        if alumno.estado_financiero == "Inhabilitado":
            subject = "Actualización de cuotas y estado financiero"
            cuotas_vencidas = ", ".join([str(cuota.nro_cuota) for cuota in cuotas])
            body += f"tienes cuotas vencidas y estás, temporalmente, inhabilitado hasta que abones la/s cuota/s {cuotas_vencidas}.  \nSaludos. \nAtte. Tesorería"
        else:
            cuotas_actualizadas = ", ".join([str(cuota.nro_cuota) for cuota in cuotas])
            subject = "Actualización de cuotas"
            body += f"se ha actualizado el monto y la fecha de vencimiento de las siguientes cuotas: {cuotas_actualizadas}. \nNo te olvides de abonar. \nSaludos. \nAtte. Tesorería"
        
        email_recipient = "tesoreriautnpruebas2024@gmail.com"  

        mensaje = configurar_mail(body, subject, email_recipient)
        try:
            enviar_email(mensaje)
            print(f"Correo enviado a: {email_recipient}")
        except Exception as e:
            print(f"Error al enviar correo a {email_recipient}: {e}")

    print("Correos enviados")


alumnos_cuota_vencida = actualizacion_de_cuotas()
#enviar_aviso_de_vencimiento(alumnos_cuota_vencida)
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

