import environ
import django
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



from django.db import models
from server.pagos.models import Cuota, CompromisoDePago, LineaDePago , FirmaCompPagoAlumno
from server.alumnos.models import Alumno
from server.materias.models import Materia, MateriaAlumno
import datetime


print(f"{datetime.datetime.now()} - tareas programadas ejecutándoseeee")


"""
def tomar_cuotas_mes_actual():
    mes_actual = datetime.now().month()
    anio_actual = datetime.now().year()
    fecha_inicio = datetime.date(anio_actual, mes_actual, 1)
    ultimo_dia_mes = (fecha_inicio.replace(month=mes % 12 + 1, day=1) - datetime.timedelta(days=1)).day
    fecha_fin = datetime.date(anio_actual, mes_actual, ultimo_dia_mes)

    cuotas_de_este_mes = Cuota.objects.filter(alumno__estado_academico="Activo",
                                            fecha_vencimiento__range=(fecha_inicio,fecha_fin),
                                            estado__in=["Impaga","Vencida","Pagada parcialmente"]
                                            ).order_by("nro_cuota")[30]

    return cuotas_de_este_mes


def alumnos_cuota_pag_parc(cuotas_de_este_mes):

    alumnos_cuota_pag_parc_dict = {}
    for cuota in cuotas_de_este_mes:
        if cuota.estado == "Pagada parcialmente":
            alumnos_cuota_pag_parc_dict[cuota.alumno.user__dni] = cuota.nro_cuota

    return alumnos_cuota_pag_parc_dict

def  alumnos_cuota_vencida(cuotas_de_este_mes):

    alumnos_cuota_vencida_dict = {}
    for cuota in cuotas_de_este_mes:
        if cuota.estado == "Vencida":
            alumnos_cuota_vencida_dict[cuota.alumno.user__dni] = cuota.nro_cuota

    return alumnos_cuota_vencida_dict


def alumnos_cuota_impaga(cuotas_de_este_mes):

    alumnos_cuota_impaga_dict = {}
    for cuota in cuotas_de_este_mes:       
        if cuota.estado == "Impaga":
            alumnos_cuota_impaga_dict[cuota.alumno.user__dni] = cuota.nro_cuota

    return alumnos_cuota_impaga_dict



"""


def actualizar_cuotas(cuotas_de_este_mes):
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

    if not ultimo_compromiso.exists() or not alumnos_firm_ult_compdepag.exists() or not alumnos_activos.exists():
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

            if cuotas_pendientes.exists():         

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
                    cuota.estado = "Vencida"
                    cuota.fecha_vencimiento = fecha_vencimiento
                    cuota.monto = monto
                    cuota.save()
                    cuotas_actualizadas.append(cuota.nro_cuota)  # Guardar el número de cuota

                # Agregar cuotas al diccionario de alumnos
                if alumno in alumnos_cuota_vencida:
                    alumnos_cuota_vencida[alumno].extend(cuotas_actualizadas)
                else:
                    alumnos_cuota_vencida[alumno] = cuotas_actualizadas


            fechas_vencimiento_monto.clear()

        print("Cuotas actualizadas")

    return alumnos_cuota_vencida

