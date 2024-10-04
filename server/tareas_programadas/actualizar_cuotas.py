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
    
    if not ultimo_compromiso:
        print("No hay compromisos de pago.")
        return {}

    alumnos_firm_ult_compdepag = FirmaCompPagoAlumno.objects.filter(compromiso_de_pago=ultimo_compromiso, alumno__in=alumnos_activos)
    hoy = timezone.now().date()
    anio_actual = hoy.year
    alumnos_cuota_vencida = {}
    cant_max_materias = 2

    if hoy.month < 3 or hoy.month > 12:
        print("Fuera de rango para actualización.")
        return {}

    cuatrimestre_analizado = 1 if hoy.month <= 7 else 2

    for alumno in alumnos_activos:
        cant_materias_alumno = MateriaAlumno.objects.filter(alumno=alumno, anio=anio_actual).count()
        cuotas_pendientes = Cuota.objects.filter(
            fecha_vencimiento__lte=hoy,
            alumno=alumno,
            estado__in=["Impaga", "Vencida", "Pagada parcialmente"],
            cuatrimestre=cuatrimestre_analizado
        ).order_by("nro_cuota")

        if cuotas_pendientes.exists():         
            fechas_vencimiento_monto = {}

            if cant_materias_alumno > cant_max_materias:
                if hoy >= ultimo_compromiso.fecha_vencimiento_2:
                    fechas_vencimiento_monto[ultimo_compromiso.fecha_vencimiento_2] = ultimo_compromiso.monto_completo_2venc
                elif hoy >= ultimo_compromiso.fecha_vencimiento_3:
                    fechas_vencimiento_monto[ultimo_compromiso.fecha_vencimiento_3] = ultimo_compromiso.monto_completo_3venc
            else:
                if hoy >= ultimo_compromiso.fecha_vencimiento_2:
                    fechas_vencimiento_monto[ultimo_compromiso.fecha_vencimiento_2] = ultimo_compromiso.monto_reducido__2venc
                elif hoy >= ultimo_compromiso.fecha_vencimiento_3:
                    fechas_vencimiento_monto[ultimo_compromiso.fecha_vencimiento_3] = ultimo_compromiso.monto_reducido_3venc
            
            for cuota in cuotas_pendientes:
                if cuota.estado in ["Impaga", "Vencida"]:
                    cuota.estado = "Vencida"
                    cuota.fecha_vencimiento = list(fechas_vencimiento_monto.keys())[0]
                    cuota.monto = list(fechas_vencimiento_monto.values())[0]
                cuota.save()

                if cuota.fecha_vencimiento < hoy:
                    alumno.estado_financiero = "Inhabilitado" 

              
                if alumno in alumnos_cuota_vencida:
                    alumnos_cuota_vencida[alumno].append(cuota)
                else:
                    alumnos_cuota_vencida[alumno] = [cuota]

            print("Cuotas actualizadas")

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








"""
def actualizacion_de_cuotas():
    alumnos_activos = Alumno.objects.filter(estado_academico="Activo")

    ultimo_compromiso = CompromisoDePago.objects.order_by('-fecha_carga_comp_pdf').first()
    
    alumnos_firm_ult_compdepag = FirmaCompPagoAlumno.objects.filter(compromiso_de_pago = ultimo_compromiso,
                                                                        alumno__in = alumnos_activos)
    hoy = timezone.now().date()
    anio_actual = hoy.year
    fechas_vencimiento_monto = {}
    alumnos_cuota_vencida = {}
    cuotas = []
    cant_max_materias = 2

    if not ultimo_compromiso or not alumnos_firm_ult_compdepag or not alumnos_activos:
        actualizar = False
    else:
        actualizar = True


    if hoy.month >= 3 and hoy.month <= 7:
        cuatrimestre_analizado = 1
    elif hoy.month > 7 and hoy.month <= 12:
        cuatrimestre_analizado = 2
    else:
        actualizar = False

    if actualizar:
        
        for alumno in alumnos_activos:

            cant_materias_alumno = MateriaAlumno.objects.filter(alumno = alumno, anio = anio_actual).count()                
            
            cuotas_pendientes = Cuota.objects.filter(fecha_vencimiento__lte = hoy, alumno = alumno,
                                                estado__in=["Impaga","Vencida","Pagada parcialmente"],
                                                cuatrimestre = cuatrimestre_analizado
                                                ).order_by("nro_cuota")

            if cuotas_pendientes:         

                if cant_materias_alumno > cant_max_materias:

                    if hoy >= ultimo_compromiso.fecha_vencimiento_2:
                        fechas_vencimiento_monto = {ultimo_compromiso.fecha_vencimiento_2 : ultimo_compromiso.monto_completo_2venc}
                    elif hoy >= ultimo_compromiso.fecha_vencimiento_3:
                        fechas_vencimiento_monto = {ultimo_compromiso.fecha_vencimiento_3 : ultimo_compromiso.monto_completo_3venc}
                else:
                    if hoy >= ultimo_compromiso.fecha_vencimiento_2:
                        fechas_vencimiento_monto = { ultimo_compromiso.fecha_vencimiento_2 : ultimo_compromiso.monto_reducido__2venc}
                    elif hoy >= ultimo_compromiso.fecha_vencimiento_3:
                        fechas_vencimiento_monto = {ultimo_compromiso.fecha_vencimiento_3 : ultimo_compromiso.monto_reducido_3venc}
                

                cuotas_actualizadas = []
                for cuota in cuotas_pendientes:
                    if cuota.estado in  ["Impaga","Vencida"]:
                        cuota.estado = "Vencida"
                        cuota.fecha_vencimiento = list(fechas_vencimiento_monto.keys())[0]
                        cuota.monto = list(fechas_vencimiento_monto.values())[0]
                    cuota.save()

                    if cuota.fecha_vencimiento.month < hoy.month:
                        alumno.estado_financiero = "Inhabilitado" 

                    cuotas_actualizadas.append(cuota)  # Guardar el número de cuota

                # Agregar cuotas al diccionario de alumnos
                if alumno in alumnos_cuota_vencida:
                    alumnos_cuota_vencida[alumno].extend(cuotas_actualizadas)
                else:
                    alumnos_cuota_vencida[alumno] = cuotas_actualizadas


            fechas_vencimiento_monto.clear()

        print("Cuotas actualizadas")
        return alumnos_cuota_vencida
    
    else:
        print("No hay cuotas que infromar")
        return {}



def enviar_aviso_de_vencimiento(alumnos_cuota_vencida):

    if alumnos_cuota_vencida != None:
    
        for alumno, cuotas in alumnos_cuota_vencida.items(): 
        
            body = f"Hola {alumno.user.full_name} "
            
            if alumno.estado_financiero == "Inhabilitado":  
                subject = "Actualización de cuotas y estado financiero"
                cuotas_vencidas = ", ".join([str(cuota.nro_cuota) for cuota in cuotas])
                body = body + f"tienes cuotas vencidas y estás, temporalmente, inhabilitado hasta que abones la/s cuota/s {cuotas_vencidas}.  \n Saludos. \n Atte. Tesoreria"
            else:
                cuotas_actualizadas = ", ".join([str(cuota.nro_cuota) for cuota in cuotas])
                subject = "Actualización de cuotas"
                body = body + f"se ha actualizado el monto y la fecha de vencimiento de las siguientes cuotas: {cuotas_actualizadas}. \n No te olvide de abonar. \n Saludos. \n Atte. Tesoreria"
            
            # Asigna el email del alumno para el envío
            #email_recipient = alumno.user.email
            
            email_recipient = "tesoreriautnpruebas2024@gmail.com"

            mensaje = configurar_mail(body, subject, email_recipient)
            try:
                enviar_email(mensaje)
                print(f"Correo enviado a: {email_recipient}")
            except Exception as e:
                print(f"Error al enviar correo a {email_recipient}: {e}")
        
        print("Correos enviados")
    else:
        print("No hay correos que enviar")"""