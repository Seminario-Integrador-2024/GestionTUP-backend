from typing import TYPE_CHECKING

from server.alumnos.models import Alumno
from server.pagos.models import Pago

if TYPE_CHECKING:
    from django.db.models.manager import BaseManager


def get_pagos_por_alumno(mes: int, anio: int) -> dict:
    """
    obtiene los pagos confirmados por alumno y el total del mes
    Args:
        mes (int): mes a buscar

    Returns:
        dict: diccionario con los pagos por alumno y
        el total del mes y subtotal por alumno
    """
    result: dict = {"total_mes": 0, "alumnos": {}}
    alumnos: BaseManager[Alumno] = Alumno.objects.all()

    for alumno in alumnos:
        al_dni = alumno.user__dni
        pagos: BaseManager[Pago] = Pago.objects.filter(
            alumno=al_dni,
            fecha__month=mes,
            fecha__year=anio,
            estado="Confirmado",
        )
        if pagos.exists():
            al_dni = str(al_dni)
            result["alumnos"].setdefault(
                al_dni,
                {"nombre": alumno.user.full_name, "total": 0, "pagos": []},
            )
            for pago_alumno in pagos:
                result["alumnos"][al_dni]["pagos"].append(
                    {"fecha": pago_alumno.fecha, "monto": pago_alumno.monto_confirmado},
                )
                result["alumnos"][al_dni]["total"] += pago_alumno.monto_confirmado
                result["total_mes"] += pago_alumno.monto_confirmado
    return result
