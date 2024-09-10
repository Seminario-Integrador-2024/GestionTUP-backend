from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from server.alumnos.api.views import AlumnosViewSet
from server.materias.api.views import MateriaViewSet
from server.pagos.api.views import CompromisoDePagoViewSet
from server.pagos.api.views import CuotaViewSet
from server.pagos.api.views import FirmaCompPagoAlumnoViewSets
from server.pagos.api.views import PagoViewSet

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


app_name = "api"
urlpatterns = router.urls
