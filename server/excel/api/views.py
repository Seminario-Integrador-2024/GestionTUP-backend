from django.http import FileResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from server.excel.api.serializers import ExcelCreateSerializer
from server.excel.api.serializers import ExcelListSerializer
from server.excel.api.serializers import SysAdminCreateSerializer
from server.excel.models import Excel


# Create your views here.
class SysacadViewSet(
    CreateModelMixin,
    ReadOnlyModelViewSet,
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

    @action(detail=True, methods=["get"], url_path="download")
    def download(self, request, *args, **kwargs):
        instance = self.get_object()
        return FileResponse(
            instance.excel,
            as_attachment=True,
            filename=instance.excel.name,
        )


class SysAdminViewSet(SysacadViewSet):
    serializer_class = ExcelListSerializer

    def get_serializer_class(self):
        if self.request.method == "POST":
            return SysAdminCreateSerializer
        return ExcelListSerializer
