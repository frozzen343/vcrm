from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from mail.utils import load_new_mail


class YourApiView(APIView):
    """
    Forced mail update
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        return Response({'message': load_new_mail()},
                        status=status.HTTP_200_OK)
