from datetime import datetime

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from server.estadisticas.utils import get_cuotas_vencidas, get_pagos_por_alumno


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
    def pagos_mes(self, request):
        """
        Retorna un JSON con los pagos confirmados por alumno y el total del mes


        Args:

            * request (request): el request.

            * month (int)[opcional]: el mes a buscar. Ingresar 0 para mes actual.

            * year (int)[opcional]: el anio a buscar. Ingresar 0 para anio actual.

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
        request_data = request.query_params
        
        if year := request_data.get("anio"):
            if year > datetime.now().year:
                return Response(
                    f"El anio {year} esta fuera de rango. intente el anio {datetime.now().year} para el anio actual",
                    status=status.HTTP_428_PRECONDITION_REQUIRED,
                )

        if month := request_data.get("mes"):
            if month < 3 or month > 12:
                return Response(
                    f"El mes {month} esta fuera de rango  intente el mes {datetime.now().month} para el mes actual",
                    status=status.HTTP_428_PRECONDITION_REQUIRED,
                )
        year = datetime.now().year if year > datetime.now().year else year
        month = datetime.now().month if month > datetime.now().month else month
        result = get_pagos_por_alumno(month, year)
        return Response(result)

    @action(
        detail=False,
        methods=["get"],
        url_path=r"cuotas_vencidas",
    )
    def cuotas_vencidas(self, request, *args, **kwargs):
        """
        cuotas_vencidas [summary] Retorna un JSON con las cuotas vencidas

        Args:
            request (request): request

            * month (int)[opcional]: el mes a buscar. Ingresar 0 para mes actual.

            * year (int)[opcional]: el anio a buscar. Ingresar 0 para anio actual.
        
        Returns: JSON: cuotas vencidas

        Responses:

            {
                "total_mes": 0,
                "alumnos": {
                    "12345678": {
                        "nombre": "Alumno Nombre",
                        "total": 0,
                        "cuotas": [
                            {
                                "fecha_vencimiento": "2021-01-01",
                                "monto": 0
                            }
                        ]
                    }
                }
            }
        """
        request_data = request.query_params
        # if year := request_data.get("anio"):
        #     if year > datetime.now().year:
        #         return Response(
        #             f"El anio {year} esta fuera de rango. intente el anio {datetime.now().year} para el anio actual",
        #             status=status.HTTP_428_PRECONDITION_REQUIRED,
        #         )

        # if month := request_data.get("mes"):
        #     if month > datetime.now().month or month < 3:
        #         return Response(
        #             f"El mes {month} esta fuera de rango  intente el mes {datetime.now().month} para el mes actual",
        #             status=status.HTTP_428_PRECONDITION_REQUIRED,
        #         )
        # year = datetime.now().year if year > datetime.now().year else year
        # month = datetime.now().month if month > datetime.now().month else month
        result = get_cuotas_vencidas()
        return Response(result)
