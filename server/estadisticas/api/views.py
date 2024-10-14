from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import EstadisticasSerializer


class EstadisticasViewSet(APIView):
    @action(detail=False, methods=["get"], url_path="pagos_mes")
    def get(self, request, *args, **kwargs):
        serializer = EstadisticasSerializer()
        return Response(serializer.data)
