from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api.views import *

router = DefaultRouter()
router.register(r"materias", MateriaViewSet)
router.register(r"materias-alumnos", MateriaAlumnoViewSet)


app_name = 'materias'
urlpatterns = [
    path("", include(router.urls)),
]
