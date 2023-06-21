from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker
from datetime import datetime

from clients.models import Client
from reports.views import make_hours_table, download_excel
from tasks.models import Task
from users.models import User


class ReportsTest(TestCase):
    def setUp(self):
        self.user = baker.make(User, is_superuser=True,
                               is_staff=True, is_active=True)
        self.client.force_login(User.objects.get(id=self.user.id))
        self.client_1 = baker.make(Client)
        baker.make(Task, hours_cost=2, status='Выполнена',
                   date_created=timezone.make_aware(datetime(2023, 5, 1)),
                   client_id=self.client_1.id, performer_id=self.user.id,
                   date_closed=timezone.make_aware(datetime(2023, 5, 1)))

    def test_make_hours_table(self):
        table = make_hours_table(month=5, year=2023)
        self.assertEqual(table.loc[self.client_1.name][self.user.last_name], 2)
        self.assertEqual(table.loc['Итого'][self.user.last_name], 2)
        self.assertEqual(table.loc['Итого']['Итого'], 2)

    def test_download_excel(self):
        response = download_excel(month=5, year=2023)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get('Content-Disposition'),
            'attachment; filename=hours_report_5_2023.xlsx')

    def test_main_reports_view(self):
        response = self.client.get(reverse('main_reports'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports/main_reports.html')

    def test_hours_reports_view(self):
        response = self.client.get(reverse('hours_reports'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports/hours_reports.html')

        data = {'month': 5, 'year': 2023}
        response = self.client.post(reverse('hours_reports'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports/hours_reports.html')
