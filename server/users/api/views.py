from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from server.users.models import User

from .serializers import UserDetailsSerializer
from .serializers import UserViewSetSerializer


class UsersViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserViewSetSerializer
    queryset = User.objects.all()
    lookup_field = "dni"

    #  @-> permite agregar acciones personalizadas a la vista
    @action(detail=False)
    def me(self, request):
        serializer = UserDetailsSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = UserDetailsSerializer(instance, context={"request": request})
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserDetailsSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)
        serializer = UserDetailsSerializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)
