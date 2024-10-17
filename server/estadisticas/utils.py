from typing import TYPE_CHECKING

from server.alumnos.models import Alumno
from server.pagos.models import Pago
from django.db.models import Sum

if TYPE_CHECKING:
    from django.db.models.manager import BaseManager


def get_pagos_por_alumno(mes: int, anio: int) -> dict:
    """
    Obtiene los pagos confirmados por alumno y el total del mes.
    Args:
        mes (int): mes a buscar
        anio (int): año a buscar

    Returns:
        dict: diccionario con los pagos por alumno,
        el total del mes y subtotal por alumno
    """
    result = {"total_mes": 0, "alumnos": {}}
    
    pagos = Pago.objects.filter(
        fecha__month=mes,
        fecha__year=anio,
        estado="Confirmado"
    ).select_related('alumno__user')
    
    for pago in pagos:
        alumno = pago.alumno
        dni = str(alumno.user.dni)
        
        if dni not in result["alumnos"]:
            result["alumnos"][dni] = {
                "nombre": alumno.user.full_name,
                "total": 0,
                "pagos": []
            }
        
        result["alumnos"][dni]["pagos"].append({
            "fecha": pago.fecha,
            "monto": pago.monto_confirmado
        })
        result["alumnos"][dni]["total"] += pago.monto_confirmado
        result["total_mes"] += pago.monto_confirmado

    return result
