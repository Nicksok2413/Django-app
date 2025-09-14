from django.contrib.auth.models import Group
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, ListCreateAPIView
from rest_framework.mixins import ListModelMixin

from .serializers import GroupSerializer


@api_view()
def hello_world_view(request: Request) -> Response:
    return Response({"message": "Hello world!"})

# *** ApiView ***

# class GroupsListView(APIView):
#     def get(self, request: Request) -> Response:
#         data = [group.name for group in Group.objects.all()]
#         return Response({"groups": data})

# *** ApiView with serialiser ***

# class GroupsListView(APIView):
#     def get(self, request: Request) -> Response:
#         serialized = GroupSerializer(Group.objects.all(), many=True)
#         return Response({"groups": serialized.data})

# *** GenericAPIView with ListModelMixin ***

# class GroupsListView(ListModelMixin, GenericAPIView):
#     queryset = Group.objects.all()
#     serializer_class = GroupSerializer
#
#     def get(self, request: Request) -> Response:
#         return self.list(request)


# *** ListCreateAPIView ***

class GroupsListView(ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer