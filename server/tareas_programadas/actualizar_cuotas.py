import datetime
from ..pagos.models import Cuota, CompromisoDePago, LineaDePago , FirmaCompPagoAlumno
from ..alumnos.models import Alumno
from ..materias.models import Materia, MateriaAlumno
import datetime


print(f"{datetime.datetime.now()} - tareas programadas ejecutándose")



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


def actualizar_cuotas(cuotas_de_este_mes):

    pass



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






def actualizar_cuotas(cuotas_de_este_mes):
    alumnos_activos = Alumno.objects.filter(estado_academico="Activo")

    ultimo_compromiso = CompromisoDePago.objects.order_by('-fecha_carga_comp_pdf').first()
    
    alumnos_firm_ult_compdepag = FirmaCompPagoAlumno.objects.filter(compromiso_de_pago = ultimo_compromiso,
                                                                        alumno__in = alumnos_activos)

    for alumno in alumnos_activos:
        materias_alumno = MateriaAlumno.objects.filter(alumno=alumno,anio=anio_actual).count()
        hora_actual = timezone.now().time()


        if hora_actual.hour >= 12:
                
            hoy = timezone.now().date()
            cuotas_pendientes = Cuota.objects.filter(fecha_vencimiento__lte=hoy)

            if cuotas_pendientes.exists():
                
                fechas_vencimiento_monto = {}

                if materias_alumno <= cant_min_materias:

                    if hoy >= ultimo_compromiso.fecha_vencimiento_2:
                        fechas_vencimiento_monto = {ultimo_compromiso.fecha_vencimiento_2 : ultimo_compromiso.monto_completo_2venc}
                    elif hoy >= ultimo_compromiso.fecha_vencimiento_3:
                        fechas_vencimiento_monto = {ultimo_compromiso.fecha_vencimiento_3 : ultimo_compromiso.monto_completo_3venc}
                else:
                    if hoy >= ultimo_compromiso.fecha_vencimiento_2:
                        fechas_vencimiento_monto = { ultimo_compromiso.fecha_vencimiento_2 : ultimo_compromiso.monto_reducido__2venc}
                    elif hoy >= ultimo_compromiso.fecha_vencimiento_3:
                        fechas_vencimiento_monto = {ultimo_compromiso.fecha_vencimiento_3 : ultimo_compromiso.monto_reducido_3venc}
        
        for cuota in cuotas_pendientes:
            cuota.estado = "Vencida"
            cuota.fecha_vencimiento = list(fechas_vencimiento_monto.keys())[0]
            cuota.monto = list(fechas_vencimiento_monto.values())[0]
            cuota.save()

    return "cuotas actualizadas"