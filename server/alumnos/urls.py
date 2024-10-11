from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api.views import AlumnosViewSet

router = DefaultRouter()
router.register(r"", AlumnosViewSet, basename='alumnos')
router.register(r'alumnos/inhabilitados/', AlumnosInhabilitadosViewSet, basename='alumnos-inhabilitados')

app_name = 'alumnos'
urlpatterns = [
    #path("alumnos/", view=AlumnosViewSet, name="alumnos"),
    path("", include(router.urls)),
    

]

