from datetime import datetime

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from server.estadisticas.utils import get_pagos_por_alumno


class EstadisticasAPIView(ViewSet):
    """
    EstadisticasAPIView

    Args:
        ViewSet (ViewSet): ViewSet from rest_framework
    """

    @action(
        detail=False,
        methods=["get"],
        url_path=r"pagos_mes/(?P<anio>\d+)/(?P<mes>\d+)",
    )
    def pagos_mes(self, request, *args, **kwargs):
        """
        Retorna un JSON con los pagos confirmados por alumno y el total del mes


        Args:

            * request (request): el request.

            * month (int)[opcional]: el mes a buscar. Ingresar 0 para mes actual.

        Returns: JSON: the payments of the month and total by user dni

        Responses:

            {
                "total_mes": 0,
                "alumnos": {
                    "12345678": {
                        "nombre": "Alumno Nombre",
                        "total": 0,
                        "pagos": [
                            {
                                "fecha": "2021-01-01",
                                "monto": 0
                            }
                        ]
                    }
                }
            }
        """
        if year := int(self.kwargs["anio"]):
            if year > datetime.now().year:
                return Response(
                    f"El anio {year} esta fuera de rango. intente el anio {datetime.now().year} para el anio actual",
                    status=status.HTTP_428_PRECONDITION_REQUIRED,
                )

        if month := int(self.kwargs["mes"]):
            if month > datetime.now().month or month < 3:
                return Response(
                    f"El mes {month} esta fuera de rango  intente el mes {datetime.now().month} para el mes actual",
                    status=status.HTTP_428_PRECONDITION_REQUIRED,
                )
        year = datetime.now().year if year == 0 or not year else year
        month = datetime.now().month if month == 0 or not month else month
        result = get_pagos_por_alumno(month, year)
        return Response(result)
