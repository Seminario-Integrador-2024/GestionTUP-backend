from rest_framework.mixins import CreateModelMixin
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import DestroyModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from server.excel.api.serializers import ExcelCreateSerializer
from server.excel.api.serializers import ExcelListSerializer
from server.excel.models import Excel


# Create your views here.
class ExcelViewSet(
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # check for context from serializer
        status_code = status.HTTP_200_OK
        if serializer.context.get("duplicates"):
            status_code = status.HTTP_206_PARTIAL_CONTENT
        return Response(serializer.data, status=status_code, headers=headers)
