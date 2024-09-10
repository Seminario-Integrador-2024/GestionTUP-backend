from rest_framework.mixins import CreateModelMixin
from rest_framework.mixins import DestroyModelMixin
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import UpdateModelMixin
from rest_framework.viewsets import GenericViewSet

from server.excel.api.serializers import ExcelCreateSerializer
from server.excel.api.serializers import ExcelListSerializer
from server.excel.models import Excel


# Create your views here.
class ExcelViewSet(
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    lookup_field = "excel"
    queryset = Excel.objects.all()

    def get_serializer_class(self):
        # check for http method
        if self.request.method == "GET":
            return ExcelListSerializer
        return ExcelCreateSerializer
