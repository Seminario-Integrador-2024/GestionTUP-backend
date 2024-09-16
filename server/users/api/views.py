from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from server.users.models import User

# from .serializers import UserViewSetSerializer

from .serializers import UserDetailsSerializer

class UsersViewSet(
    RetrieveModelMixin,
    ListModelMixin,
    UpdateModelMixin,
    GenericViewSet,
):
    # serializer_class = UserViewSetSerializer
    serializer_class = UserDetailsSerializer

    queryset = User.objects.all()
    lookup_field = "pk"

    @action(detail=False)
    def me(self, request):
        serializer = UserViewSetSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)
