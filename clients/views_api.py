from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from clients.models import Client
from clients.serializers import ClientListSerializer


class ClientListAPIView(ListAPIView):
    """
    Client list view
    """
    queryset = Client.objects.order_by('name').all()
    serializer_class = ClientListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
