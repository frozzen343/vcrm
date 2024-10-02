from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from clients.models import Client, Contact
from clients.serializers import ClientListSerializer


class ClientListAPIView(ListAPIView):
    """
    Client list view
    """
    queryset = Client.objects.order_by('name').all()
    serializer_class = ClientListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None


class AttachContactToClient(APIView):
    """
    Attaches contact to a client
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if self.request.user.has_perm('clients.change_contact'):
            contact = request.data.get('contact')
            client = int(request.data.get('client'))
            fio = request.data.get('fio', None)
            if contact and client:
                Contact.objects.get_or_create(contact=contact, fio=fio,
                                              client_id=client)
                return Response({'detail': 'Done.'})
            return Response({'detail': 'Need contact and client fields'})
        return Response({'detail': 'Access denied!'})
