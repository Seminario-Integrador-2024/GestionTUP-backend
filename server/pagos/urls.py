# core/urls.py
from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from .api.views import CompromisoDePagoViewSet
from .api.views import CuotaViewSet
from .api.views import FirmarCompromisoView
from .api.views import FirmasDeUnAlumnoView
from .api.views import PagoViewSet
from .api.views import AlumnosFirmaronUltimoCompromisoView
from .api.views import AlumnosNoFirmaronUltimoCompromisoView

router = DefaultRouter()
"""router.register(r"compromisos", CompromisoDePagoViewSet, basename="compromisos")
router.register(r"pagos", PagoViewSet, basename="pagos")
router.register(r"cuotas", CuotaViewSet, basename="cuotas")
"""

app_name = "pagos"

urlpatterns = [
    path("", include(router.urls)),
    path(
        "compromisos/archivo/<int:pk>/",
        CompromisoDePagoViewSet.as_view({"get": "retrieve_pdf"}),
        name="retrieve-pdf",
    ),
    path(
        "firmas-de-alumno/<int:alumno_id>/",
        FirmasDeUnAlumnoView.as_view({"get": "list"}),
        name="firmas-de-alumno",
    ),
    path(
        "firmar-compromiso/<int:alumno_id>/",
        FirmarCompromisoView.as_view(),
        name="firmar-compromiso",
    ),
    path(
        "alumnos-firmaron-ultimo-compromiso/",
        AlumnosFirmaronUltimoCompromisoView.as_view({"get": "list"}),
        name="alumnos-firmaron-ultimo-compromiso",
    ),
    path(
        "alumnos-no-firmaron-ultimo-compromiso/",
        AlumnosNoFirmaronUltimoCompromisoView.as_view({"get": "list"}),
        name="alumnos-no-firmaron-ultimo-compromiso",
    ),
]

urlpatterns += router.urls
