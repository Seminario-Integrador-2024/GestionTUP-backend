# core/urls.py
from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter

from .api.views import CompromisoDePagoViewSet
from .api.views import CuotaViewSet
from .api.views import FirmarCompromisoView
from .api.views import FirmasDeUnAlumnoView
from .api.views import PagoViewSet
from .api.views import UltimoCompromisoDePago

router = DefaultRouter()
router.register(r"compromisos", CompromisoDePagoViewSet)
router.register(r"pagos", PagoViewSet)
router.register(r"cuotas", CuotaViewSet)


app_name = "pagos"
urlpatterns = [
    path("", include(router.urls)),
    path(
        "compromisos/archivo/<int:pk>/",
        CompromisoDePagoViewSet.as_view({"get": "retrieve_pdf"}),
        name="retrieve_pdf",
    ),
    path(
        "ultimo-compr-de-pag/",
        UltimoCompromisoDePago.as_view(),
        name="ultimo-compromiso-de-pago",
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
]

urlpatterns += router.urls
