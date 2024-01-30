from django.test import TestCase
from django.urls import reverse
from model_bakery import baker

from clients.models import Client
from tasks.models import Task, Comment
from tasks.views import comment_if_changes
from users.models import User


class TestTasks(TestCase):
    """Url tests"""

    def setUp(self):
        self.user = baker.make(User, is_superuser=False,
                               is_staff=False, is_active=True)
        self.other_user = baker.make(User, is_superuser=False,
                                     is_staff=False, is_active=True)
        self.client.force_login(User.objects.get(id=self.user.id))

    # def test_task_list_view(self):
    #     """TaskListView test"""
    #     baker.make(Task, _quantity=20)
    #     response = self.client.get(reverse('task_list'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'tasks/task_list.html')
    #
    #     self.assertIsInstance(response.context['view'], TaskListView)
    #     self.assertIsInstance(response.context['filter'], TaskFilter)
    #     self.assertEqual(
    #         response.context['paginator'].per_page, TaskListView.paginate_by)
    #     self.assertEqual(len(response.context['tasks']), 10)

    def test_task_create_view(self):
        """TaskCreateView test"""
        client = baker.make(Client)
        data = {
            'title': 'Test task',
            'performer': self.user.pk,
            'status': 'В работе',
            'hours_cost': 2,
            'contacts': 'test@example.com',
            'client': client.id,
            'fire': False,
            'drive': True,
            'description': 'Test task description',
        }
        response = self.client.post(reverse('task_create'), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('task_list'))

        task = Task.objects.last()
        self.assertEqual(task.title, data['title'])
        self.assertEqual(task.performer, self.user)
        self.assertEqual(task.status, data['status'])
        self.assertEqual(task.hours_cost, data['hours_cost'])
        self.assertEqual(task.contacts, data['contacts'])
        self.assertEqual(task.client.id, data['client'])
        self.assertEqual(task.fire, data['fire'])
        self.assertEqual(task.drive, data['drive'])
        self.assertEqual(task.description, data['description'])

        comment = Comment.objects.last()
        self.assertEqual(comment.task, task)
        self.assertEqual(comment.comment,
                         (f'Пользователь <b>{self.user.first_name} '
                          f'{self.user.last_name}</b> создал задачу'))

    def test_task_edit_view_get(self):
        """TaskEditView test"""
        task = baker.make(Task, performer=self.user)
        response = self.client.get(reverse('task_edit',
                                           kwargs={'pk': task.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('comments', response.context)
        self.assertIn('form2', response.context)
        self.assertIn('contacts', response.context)
        self.assertTemplateUsed(response, 'tasks/task_edit.html')

    def test_task_edit_view_get_permission_error(self):
        task = baker.make(Task, performer=self.other_user)
        response = self.client.get(reverse('task_edit',
                                           kwargs={'pk': task.pk}))
        self.assertEqual(response.status_code, 403)

    def test_task_edit_view_post(self):
        """TaskEditView test"""
        task = baker.make(Task, performer=self.user)
        data = {
            'performer': self.user.pk,
            'status': 'Выполнена',
            'hours_cost': 10,
            'description': 'New description'
        }

        response = self.client.post(reverse('task_edit',
                                            kwargs={'pk': task.pk}), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Task.objects.get(pk=task.pk).hours_cost,
                         data['hours_cost'])
        self.assertEqual(Task.objects.get(pk=task.pk).status, data['status'])

    def test_task_edit_view_post_perm_error(self):
        task = baker.make(Task, status='В работе', performer=self.user)
        data = {'performer': self.other_user.pk,
                'status': 'Выполнена',
                'hours_cost': 10,
                'description': 'New description'}
        response = self.client.post(reverse('task_edit',
                                            kwargs={'pk': task.pk}), data=data)
        self.assertEqual(response.status_code, 403)

    def test_task_edit_view_comments(self):
        """TaskEditView test"""
        task = baker.make(Task, performer=self.user)
        data = {'comment': 'Test comment',
                'add_comment': 'Добавить'}
        response = self.client.post(reverse('task_edit',
                                            kwargs={'pk': task.pk}), data=data)
        self.assertEqual(response.status_code, 302)

        comment = Comment.objects.last()
        self.assertEqual(comment.task, task)
        self.assertEqual(comment.comment, data['comment'])

    def test_task_edit_view_buttons(self):
        """TaskEditView test"""
        task = baker.make(Task, performer=self.user)
        url = reverse('task_edit', kwargs={'pk': task.pk})

        response = self.client.post(url, {'edit_buttons': 'Принять'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Task.objects.get(pk=task.pk).status, 'В работе')

        response = self.client.post(url, {'edit_buttons': 'Отложено'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Task.objects.get(pk=task.pk).status, 'Отложена')

        response = self.client.post(url, {'edit_buttons': 'Не задача'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Task.objects.get(pk=task.pk).status, 'Не задача')

        response = self.client.post(url, {'edit_buttons': 'Выполнено'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Task.objects.get(pk=task.pk).status, 'Выполнена')

    def test_task_edit_view_buttons_perm_error(self):
        task = baker.make(Task, performer=self.user, status='Выполнена')
        url = reverse('task_edit', kwargs={'pk': task.pk})

        response = self.client.post(url, {'edit_buttons': 'Выполнено'})
        self.assertEqual(response.status_code, 403)

    def test_comment_if_changes(self):
        task = baker.make(Task, status='Новая')
        fields = ['status']

        comment_if_changes(task, self.user, fields)

        comment = Comment.objects.last()
        self.assertEqual(
            comment.comment,
            f'<p>Пользователь <b>{self.user.first_name} '
            f'{self.user.last_name}</b> присвоил статус задачи '
            f'<b>{task.status}</b></p>')
