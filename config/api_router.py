from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter
from django.urls import path, include
from server.alumnos.api.views import AlumnosViewSet
from server.excel.api.views import ExcelViewSet
from server.materias.api.views import MateriaViewSet
from server.pagos.api.views import CompromisoDePagoViewSet
from server.pagos.api.views import CuotaViewSet
from server.pagos.api.views import FirmaCompPagoAlumnoViewSets
from server.pagos.api.views import PagoViewSet
from server.pagos.api.views import UltimoCompromisoDePagoViewSet
from server.pagos.api.views import FirmarCompromisoView
from server.pagos.api.views import FirmasDeUnAlumnoView
from server.pagos.api.views import CuotaDeUnAlumnoViewSet
from server.pagos.api.views import PagoDeUnAlumnoViewSet 
from server.pagos.api.views import PagoDeUnAlumnoRetrieveViewSet

# agregar las vistas de de cada app en forma de router.
# el import debe seguir el siguiente formato:
# from server.<app>.api.views import <ViewSet>
from server.users.api.views import UsersViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

# para cada app el formato es :
# router.register("<path>", <ViewSet>, basename="<name>")


router.register("users", UsersViewSet, basename="user")
router.register("alumnos", AlumnosViewSet, basename="alumno")
router.register("pagos", PagoViewSet, basename="pago")
router.register("cuotas", CuotaViewSet, basename="cuota")
router.register("compromisos", CompromisoDePagoViewSet, basename="compromiso")
router.register("firmas", FirmaCompPagoAlumnoViewSets, basename="firma")
router.register("materias", MateriaViewSet, basename="materia")
router.register("excels", ExcelViewSet, basename="excel")


app_name = "api"

# Urls "especificos" (que no heredan de ModelViewSet)
# formato: path("ruta/", <View>.as_view(), name="<name>")

# url de pagos
url_pagos = [
    path("compromisos/archivo/<int:pk>/", CompromisoDePagoViewSet.as_view({"get": "retrieve_pdf"}), name="retrieve_pdf"),
    path("ultimo-compromiso-de-pago/", UltimoCompromisoDePagoViewSet.as_view(), name="ultimo-compromiso-de-pago"),
    path("firmas/firmas-de-alumno/<int:alumno_id>/", FirmasDeUnAlumnoView.as_view({"get": "list"}), name="firmas-de-alumno"),
    path("firmas/firmar-compromiso/<int:alumno_id>/", FirmarCompromisoView.as_view(),name="firmar-compromiso"),
    path("cuotas/alumno/<int:alumno_id>/", CuotaDeUnAlumnoViewSet.as_view({"get": "list"}), name="cuotas-de-alumno"),
    path("pagos/alumno/<int:alumno_id>",PagoDeUnAlumnoViewSet.as_view(), name = "pago-de-un-alumno"),
    path("pagos/alumno/resumen_pagos/<int:alumno_id>",PagoDeUnAlumnoRetrieveViewSet.as_view({"get": "list"}), name = "pago-de-un-alumno-retrive"),
]


urlpatterns = router.urls + url_pagos
