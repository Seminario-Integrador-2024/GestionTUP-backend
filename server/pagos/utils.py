#django imports
from django.utils import timezone
from django.db.models import Sum

#python imports
import time
import calendar
from datetime import date

#pagos imports
from ..alumnos.models import Alumno
from ..materias.models import MateriaAlumno
from .models import Cuota, CompromisoDePago


#comentario
def fecha_primer_vencimiento(ultimo_compromiso, mes=0):
    fecha_actual = timezone.now().date()
    anio_actual = fecha_actual.year
    mes_actual = fecha_actual.month
    dia_actual = fecha_actual.day

    nuevo_mes = mes_actual + mes
    while nuevo_mes > 12:
        nuevo_mes -= 12
        anio_actual += 1

    if mes == 0:
        if dia_actual <= ultimo_compromiso.fecha_vencimiento_1:
            dia_prox_vencimiento = ultimo_compromiso.fecha_vencimiento_1
        elif dia_actual > ultimo_compromiso.fecha_vencimiento_1 and dia_actual <= ultimo_compromiso.fecha_vencimiento_2:
            dia_prox_vencimiento = ultimo_compromiso.fecha_vencimiento_2
        else:
            dia_prox_vencimiento = ultimo_compromiso.fecha_vencimiento_3
    else:
         dia_prox_vencimiento = ultimo_compromiso.fecha_vencimiento_1


    ultimo_dia_mes = calendar.monthrange(anio_actual, nuevo_mes)[1]

    if dia_prox_vencimiento > ultimo_dia_mes:
        dia_prox_vencimiento = ultimo_dia_mes

    fecha_vencimiento = date(anio_actual, nuevo_mes, dia_prox_vencimiento)
    return fecha_vencimiento



def cargar_matricula_anual(alumno_id,ultimo_compromiso):
    alumno = Alumno.objects.get(user=alumno_id)
    # Verificar si ya existe una cuota de matrícula para este año
    anio_actual = timezone.now().year
    matricula_existente = Cuota.objects.filter(
        alumno=alumno_id,
        tipo="Matrícula",
        fecha_vencimiento__year=anio_actual
    ).exists()

    if not matricula_existente:
        # Si no existe, crear la cuota de matrícula
        
        fecha_vencimiento = fecha_primer_vencimiento(ultimo_compromiso)

        nro_cuota_ultima = nro_ultima_cuota(alumno_id)


        Cuota.objects.create(
            nro_cuota = 0,
            monto = ultimo_compromiso.matricula,
            compdepago = ultimo_compromiso,
            estado = "Impaga",
            fecha_vencimiento = fecha_primer_vencimiento(ultimo_compromiso),
            fecha_pago_devengado = timezone.now().date(),
            tipo = "Matrícula",
            alumno = alumno
        )


def cargar_cuotas_alumno(alumno_id,ultimo_compromiso):
    alumno = Alumno.objects.get(user=alumno_id)
    anio_actual = timezone.now().year
    materias_alumno = MateriaAlumno.objects.filter(id_alumno_id=alumno_id,anio=anio_actual).count()
    cant_min_materias = 2
    #estado_cuota = ""

    if materias_alumno <= cant_min_materias:
        if timezone.now().day <= ultimo_compromiso.fecha_vencimiento_1:
            monto = ultimo_compromiso.cuota_reducida
            #estado_cuota = "Impaga"
        elif timezone.now().day > ultimo_compromiso.fecha_vencimiento_1 and timezone.now().day <= ultimo_compromiso.fecha_vencimiento_2:
            monto = ultimo_compromiso.cuota_reducida_2venc
            #estado_cuota = "Vencida"
        else:
            monto = ultimo_compromiso.cuota_reducida_3venc
            #estado_cuota = "Vencida"
    else:
        if timezone.now().day <= ultimo_compromiso.fecha_vencimiento_1:
            monto = ultimo_compromiso.monto_completo
            #estado_cuota = "Impaga"
        elif timezone.now().day > ultimo_compromiso.fecha_vencimiento_1 and timezone.now().day <= ultimo_compromiso.fecha_vencimiento_2:
            monto = ultimo_compromiso.monto_completo_2venc
            #estado_cuota = "Vencida"
        else:
            monto = ultimo_compromiso.monto_completo_3venc
            #estado_cuota = "Vencida"




    # Crear matrícula anual
    cargar_matricula_anual(alumno_id,ultimo_compromiso)

    # Crea una nueva fecha con el día fijado al 10 del mes actual
    #fecha_vencimiento = fecha_primer_vencimiento(ultimo_compromiso)

    #Esto es para mantener el orden de las cuotas
    nro_cuota_ultima = nro_ultima_cuota(alumno_id)


    # Crear 5 cuotas mensuales 
    for i in range(1, 6):
        if i == 1:
            monto_a_usar = monto  
        else:
            if materias_alumno > cant_min_materias:
                monto_a_usar = ultimo_compromiso.monto_completo
            else:
                monto_a_usar = ultimo_compromiso.cuota_reducida 

        # Crear la cuota
        Cuota.objects.create(
            nro_cuota=nro_cuota_ultima + i,
            monto=monto_a_usar,
            compdepago=ultimo_compromiso,
            estado="Impaga",  # Se mantiene el estado como 'Impaga'
            fecha_vencimiento=fecha_primer_vencimiento(ultimo_compromiso, i-1),
            fecha_pago_devengado=timezone.now(),
            tipo="Cuota",
            alumno=alumno
        )


def generar_cuotas(alumno_id,ultimo_compromiso):

    cargar_cuotas_alumno(alumno_id,ultimo_compromiso)

def nro_ultima_cuota(alumno_id):
    anio_actual = timezone.now().year
    
    ultima_cuota = Cuota.objects.filter(alumno=alumno_id).order_by('nro_cuota').last()
    cant_cuotas_por_anio = Cuota.objects.filter(alumno=alumno_id, fecha_vencimiento__year=anio_actual).count()


    if cant_cuotas_por_anio >= 11:
        return 0 

    return ultima_cuota.nro_cuota if ultima_cuota else 0

