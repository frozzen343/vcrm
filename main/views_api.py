from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone


class GetTimeAPIView(APIView):
    def get(self, request):
        current_datetime = timezone.now()
        current_year = current_datetime.year
        current_month = current_datetime.month
        time = current_datetime.strftime("%H:%M")
        return Response({'time': time,
                         'month': current_month,
                         'year': current_year})
