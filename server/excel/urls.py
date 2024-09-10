from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from .api.views import ExcelViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()
router.register(r"excels", ExcelViewSet)
