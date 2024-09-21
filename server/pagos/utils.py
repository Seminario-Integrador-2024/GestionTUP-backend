#django imports
from django.utils import timezone
from django.db.models import Sum

#python imports
import time
from datetime import date

#pagos imports
from ..alumnos.models import Alumno
from ..materias.models import MateriaAlumno
from .models import Cuota, CompromisoDePago


# Carga las cuotas del alumno segun las materias que este tenga
# Se debe crear una matrícula anual y 10 cuotas mensuales, los montos son fijados en marzo, con actualización en julio.
# Los montos dependen de si el alumno tiene 2 o mas materias o mas. Si tiene 2 o menos materias, se le cobra el monto_reducido, si tiene mas de 2 materias, se le cobra el monto_completo.

# Las cuotas se deben abonar en los periodos 1-10 (con monto_comprleto o reducido) del 10-15 (monto_completo_2venc o monto_reducido__2venc)
#  y 15-30( monto_completo_3venc o monto_reducido_3venc )

def fecha_primer_vencimiento(ultimo_compromiso):
    fecha_actual = timezone.now().date()
    anio_actual = fecha_actual.year
    mes_actual = fecha_actual.month

    # Crea una nueva fecha con el día fijado al 10 del mes actual
    fecha_vencimiento = date(anio_actual, mes_actual, ultimo_compromiso.fecha_vencimiento_1)
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
            nro_cuota = nro_cuota_ultima + 1,
            monto = ultimo_compromiso.matricula,
            compdepago = ultimo_compromiso,
            estado = "Impaga",
            fecha_vencimiento = fecha_vencimiento ,
            fecha_pago_devengado = timezone.now().date(),
            tipo = "Matrícula",
            alumno = alumno
        )


def cargar_cuotas_alumno(alumno_id,ultimo_compromiso):
    alumno = Alumno.objects.get(user=alumno_id)
    anio_actual = timezone.now().year
    materias_alumno = MateriaAlumno.objects.filter(id_alumno_id=alumno_id,anio=anio_actual).count()
    cant_min_materias = 2

    # Determinar el monto a pagar basado en la cantidad de materias
    if materias_alumno <= cant_min_materias:
        monto_base = ultimo_compromiso.cuota_reducida
        monto_2venc = ultimo_compromiso.cuota_reducida_2venc
        monto_3venc = ultimo_compromiso.cuota_reducida_3venc
    else:
        monto_base = ultimo_compromiso.monto_completo
        monto_2venc = ultimo_compromiso.monto_completo_2venc
        monto_3venc = ultimo_compromiso.monto_completo_3venc


    # Crear matrícula anual
    cargar_matricula_anual(alumno_id,ultimo_compromiso)

    # Crea una nueva fecha con el día fijado al 10 del mes actual
    fecha_vencimiento = fecha_primer_vencimiento(ultimo_compromiso)


    nro_cuota_ultima = nro_ultima_cuota(alumno_id)

    # Crear 5 cuotas mensuales 
    for i in range(1, 6):
        Cuota.objects.create(
            nro_cuota=nro_cuota_ultima+i,
            monto=monto_base,
            compdepago=ultimo_compromiso,
            estado="Impaga",
            fecha_vencimiento=fecha_vencimiento,
            fecha_pago_devengado=timezone.now(),
            tipo="Cuota",
            alumno=alumno
        )


def generar_cuotas(alumno_id,ultimo_compromiso):

    cargar_cuotas_alumno(alumno_id,ultimo_compromiso)

def nro_ultima_cuota(alumno_id):
    ultima_cuota = Cuota.objects.filter(alumno=alumno_id).order_by('nro_cuota').last()
    if ultima_cuota:
        return ultima_cuota.nro_cuota
    else:
        return 0




#---------------------- Seguir completando esta funcion después ----------------------
def actualizar_cuotas(alumno_id,ultimo_compromiso):
    materias_alumno = MateriaAlumno.objects.filter(alumno=alumno,anio=anio_actual).count()
    hora_actual = timezone.now().time()


    if hora_actual.hour >= 12:
            
        hoy = timezone.now().date()
        cuotas_pendientes = Cuota.objects.filter(estado="Pendiente",fecha_vencimiento__lte=hoy)

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

