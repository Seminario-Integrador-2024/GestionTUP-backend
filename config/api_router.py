from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from server.alumnos.api.views import AlumnosQueNoPagaronCuotaViewSet
from server.alumnos.api.views import AlumnosQuePagaronCuotaViewSet
from server.alumnos.api.views import AlumnosViewSet
from server.alumnos.api.views import AlumnosInhabilitadosViewSet, AlumnosAInhabilitarViewSet 
from server.excel.api.views import SysacadViewSet
from server.excel.api.views import SysAdminViewSet
from server.materias.api.views import MateriaViewSet
from server.pagos.api.views import AlumnosFirmaronUltimoCompromisoView
from server.pagos.api.views import AlumnosNoFirmaronUltimoCompromisoView
from server.pagos.api.views import CompromisoDePagoViewSet
from server.pagos.api.views import CuotaDeUnAlumnoViewSet
from server.pagos.api.views import CuotasImpagasDeUnAlumnoViewSet
from server.pagos.api.views import CuotaViewSet
from server.pagos.api.views import FirmaCompPagoAlumnoViewSets
from server.pagos.api.views import FirmarCompromisoView
from server.pagos.api.views import FirmasDeUnAlumnoView
from server.pagos.api.views import PagoDeUnAlumnoRetrieveViewSet
from server.pagos.api.views import PagoDeUnAlumnoViewSet
from server.pagos.api.views import PagoViewSet
from server.pagos.api.views import UltimoCompromisoDePagoViewSet

# agregar las vistas de de cada app en forma de router.
# el import debe seguir el siguiente formato:
# from server.<app>.api.views import <ViewSet>
from server.users.api.views import UsersViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

# para cada app el formato es :
# router.register("<path>", <ViewSet>, basename="<name>")


router.register("alumnos", AlumnosViewSet, basename="alumno")
router.register("compromisos", CompromisoDePagoViewSet, basename="compromiso")
router.register("cuotas", CuotaViewSet, basename="cuota")
router.register("excels/sysacad", SysacadViewSet, basename="excel-sysacad")
router.register("excels/sysadmin", SysAdminViewSet, basename="excel-sysadmin")
router.register("firmas", FirmaCompPagoAlumnoViewSets, basename="firma")
router.register("materias", MateriaViewSet, basename="materia")
router.register("pagos", PagoViewSet, basename="pago")
router.register("users", UsersViewSet, basename="user")


app_name = "api"

# Urls "especificos" (que no heredan de ModelViewSet)
# formato: path("ruta/", <View>.as_view(), name="<name>")

# url de pagos
url_pagos = [
    path(
        "compromisos/archivo/<int:pk>/",
        CompromisoDePagoViewSet.as_view({"get": "retrieve_pdf"}),
        name="retrieve_pdf",
    ),
    path(
        "ultimo-compromiso-de-pago/",
        UltimoCompromisoDePagoViewSet.as_view(),
        name="ultimo-compromiso-de-pago",
    ),
    path(
        "firmas/firmas-de-alumno/<int:alumno_id>/",
        FirmasDeUnAlumnoView.as_view({"get": "list"}),
        name="firmas-de-alumno",
    ),
    path(
        "firmas/firmar-compromiso/<int:alumno_id>/",
        FirmarCompromisoView.as_view(),
        name="firmar-compromiso",
    ),
    path(
        "firmantes/alumnos-firmaron-ultimo-compromiso/",
        AlumnosFirmaronUltimoCompromisoView.as_view({"get": "list"}),
        name="alumnos-firmaron-ultimo-compromiso",
    ),
    path(
        "firmantes/alumnos-no-firmaron-ultimo-compromiso/",
        AlumnosNoFirmaronUltimoCompromisoView.as_view({"get": "list"}),
        name="alumnos-no-firmaron-ultimo-compromiso",
    ),
    path(
        "cuotas/alumno/<int:alumno_id>/",
        CuotaDeUnAlumnoViewSet.as_view({"get": "list"}),
        name="cuotas-de-alumno",
    ),
    path(
        "cuotas/alumno/<int:alumno_id>/impagas/",
        CuotasImpagasDeUnAlumnoViewSet.as_view({"get": "list"}),
        name="cuotas-impagas-de-alumno",
    ),
    path(
        "pagos/alumno/<int:alumno_id>/",
        PagoDeUnAlumnoViewSet.as_view(),
        name="pago-de-un-alumno",
    ),
    path(
        "pagos/alumno/resumen_pagos/<int:alumno_id>/",
        PagoDeUnAlumnoRetrieveViewSet.as_view({'get': 'list'}),
        name="pago-de-un-alumno-retrive",
    ),
]

url_alumnos = [
    path(
        "alumnos/pagaron-cuota/<str:mes_anio>/",
        AlumnosQuePagaronCuotaViewSet.as_view({"get": "list"}),
        name="alumnos-pagaron-cuota",
    ),
    path(
        "alumnos/no-pagaron-cuota/<str:mes_anio>/",
        AlumnosQueNoPagaronCuotaViewSet.as_view({"get": "list"}),
        name="alumnos-no-pagaron-cuota",
    ),
    path(
        "alumnos/inhabilitados",
        AlumnosInhabilitadosViewSet.as_view({"get": "list"}),
        name="alumnos-inhabilitados",
    ),
    path(
        "alumnos/alumnos-a-inhabilitar",
        AlumnosAInhabilitarViewSet.as_view({"get": "list"}),
        name="alumnos-a-inhabilitar",
    ),
    path(
        "alumnos/alumno-a-inhabilitar/<int:legajo>/",
        AlumnosAInhabilitarViewSet.as_view({"delete": "destroy"}),
        name="alumno-a-inhabilitar",
    ),
]

urlpatterns = router.urls + url_pagos + url_alumnos
