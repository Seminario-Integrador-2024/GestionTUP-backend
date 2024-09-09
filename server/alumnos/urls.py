from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api.views import AlumnosViewSet

router = DefaultRouter()
router.register(r"", AlumnosViewSet, basename='alumnos')

app_name = 'alumnos'
urlpatterns = [
    #path("alumnos/", view=AlumnosViewSet, name="alumnos"),
    path("", include(router.urls)),

]

