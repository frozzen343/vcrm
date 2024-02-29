from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied
from django.db.models import Sum
from django.http import HttpResponse
from django.utils import timezone
from io import BytesIO
import pandas as pd

from clients.models import Client
from reports.utils import make_hours_table
from tasks.models import Task
from users.models import User


class HoursReportAPIView(APIView):
    def get(self, request):
        if not self.request.user.has_perm('perms.view_users_report'):
            raise PermissionDenied

        month = request.GET.get('month')
        year = request.GET.get('year')
        report_hours = (Task.objects
                        .filter(date_closed__month=month,
                                date_closed__year=year,
                                # performer__isnull=False,
                                status='Выполнена')
                        .values('performer__id', 'client__id')
                        .annotate(total_hours=Sum('hours_cost')))

        if len(report_hours) == 0:
            return Response({'detail': 'Данных ещё нет'}, status=400)

        data = {}
        for report in report_hours:
            performer_id = report['performer__id']
            client_name = report['client__id']
            total_hours = report['total_hours']
            if client_name not in data:
                data[client_name] = {}
            data[client_name][performer_id] = total_hours

        users = (User.objects
                 .filter(is_active=True)
                 .values('first_name', 'last_name', 'id')
                 .all()
                 .order_by('first_name'))
        report_clients_id = report_hours.values_list('client_id',
                                                     flat=True).distinct()
        clients = (Client.objects
                   .filter(id__in=report_clients_id)
                   .values('name', 'id')
                   .all()
                   .order_by('name'))

        return Response({'clients': clients, 'users': users, 'data': data})


class DownloadExcelAPIView(APIView):
    def get(self, request):
        month = request.GET.get('month', timezone.now().month)
        year = request.GET.get('year', timezone.now().year)

        df = make_hours_table(month, year)

        if df is not None:
            with BytesIO() as b:
                with pd.ExcelWriter(b) as writer:
                    df.to_excel(writer, sheet_name="Расчет часов")

                filename = f'hours_report_{month}_{year}.xlsx'

                res = HttpResponse(
                    b.getvalue(),
                    content_type='application/vnd.openxmlformats-'
                                 'officedocument.spreadsheetml.sheet'
                )
                res['Content-Disposition'] = f'attachment; filename={filename}'
                return res
        else:
            return Response({'detail': 'Данных ещё нет'}, status=400)
