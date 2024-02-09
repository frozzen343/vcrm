from django.test import TestCase
from django.urls import reverse
# from django.utils import timezone
from model_bakery import baker

from tasks.models import Task
from users.models import User


class MainTest(TestCase):
    def setUp(self):
        self.user = baker.make(User, is_active=True)
        self.client.force_login(User.objects.get(id=self.user.id))
        baker.make(Task)

    def test_main_view(self):
        response = self.client.get(reverse('main'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/main.html')
        self.assertEqual(response.context['count_new_tasks'], 1)

    # def test_get_time(self):
    #     response = self.client.get(reverse('get_time'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertJSONEqual(str(response.content, encoding='utf8'),
    #                          {'time': timezone.now().strftime("%H:%M")})
