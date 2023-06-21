from django.test import TestCase
from django.urls import reverse
from model_bakery import baker
from django.contrib.auth.models import Group

from users.models import User


class TestPermissions(TestCase):
    """Url tests"""

    def test_anonymous_user(self):
        self.client.logout()
        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('user_create'))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('user_edit', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('user_del', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('user_changepass',
                                           kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse('group_add',
                                           kwargs={'user_id': 1,
                                                   'group_id': 1}))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse('group_del',
                                           kwargs={'user_id': 1,
                                                   'group_id': 1}))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse('profile', kwargs={'pk': 50}))
        self.assertEqual(response.status_code, 403)
        # response = self.client.get(reverse('background'))
        # self.assertEqual(response.status_code, 302)

    def test_without_permissions(self):
        """Whithout permissions test"""
        self.user = baker.make(User, is_superuser=False, is_staff=False)
        self.client.force_login(User.objects.get(id=self.user.id))

        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse('user_create'))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse('user_edit', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse('user_del', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse('user_changepass',
                                           kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse('group_add',
                                           kwargs={'user_id': 1,
                                                   'group_id': 1}))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse('group_del',
                                           kwargs={'user_id': 1,
                                                   'group_id': 1}))
        self.assertEqual(response.status_code, 403)
        response = self.client.get(reverse('profile', kwargs={'pk': 5000}))
        self.assertEqual(response.status_code, 403)


class TestProfileUser(TestCase):
    """Profile tests"""

    def setUp(self):
        self.user = baker.make(User, is_superuser=False,
                               is_staff=False, is_active=True)

    def test_login_view(self):
        """UserLoginView test"""
        password = self.user.password
        self.user.set_password(password)
        self.user.save()
        form_data = {
            'username': self.user.email,
            'password': password,
        }
        response = self.client.post(reverse('login'), data=form_data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('main'))

    def test_login_view_invalid(self):
        """UserLoginView with incorrect data test"""
        form_data = {
            'username': self.user.email,
            'password': 'password',
        }
        response = self.client.post(reverse('login'), data=form_data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_change_background(self):
        self.client.force_login(User.objects.get(id=self.user.id))
        img_url = 'backgrounds/nissan.jpg'

        response = self.client.post(reverse('background'), {'img': img_url})
        self.user.refresh_from_db()
        self.assertRedirects(response, reverse('main'))
        self.assertEqual(self.user.background.url, '/media/'+img_url)
        self.assertEqual(response.status_code, 302)

    def test_update_user_profile(self):
        self.client.force_login(User.objects.get(id=self.user.id))
        url = reverse('profile', kwargs={'pk': self.user.pk})
        notify_new_tasks = True
        response = self.client.post(url, {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@test.com',
            'notify_new_tasks': notify_new_tasks,
        })

        self.assertRedirects(response, url)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')
        self.assertEqual(self.user.email, 'testuser@test.com')
        self.assertEqual(self.user.notify_new_tasks, notify_new_tasks)


class TestManageUsers(TestCase):
    """CRUD users tests"""

    def setUp(self):
        self.user_admin = baker.make(User, is_superuser=True, is_staff=True)
        self.user = baker.make(User)
        self.group = Group.objects.create(name='Test Group')
        self.client.force_login(User.objects.get(id=self.user_admin.id))

    def test_list_users(self):
        """UserListView test"""
        response = self.client.get(reverse('user_list'))
        self.assertIn(self.user, response.context['users'])
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/user_list.html')

    def test_user_create_view(self):
        """UserCreateView test"""
        form_data = {
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password1': 'password123!#',
            'password2': 'password123!#',
        }
        response = self.client.post(reverse('user_create'), data=form_data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('user_list'))
        self.assertTrue(User.objects.filter(email='newuser@example.com')
                            .exists())

    def test_user_edit_view(self):
        """UserEditView test"""
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
        }
        response = self.client.post(reverse('user_edit',
                                            kwargs={'pk': self.user.pk}),
                                    data=form_data,
                                    follow=True)
        self.assertTrue(User.objects.filter(email='john.doe@example.com')
                        .exists())
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('user_list'))

    def test_user_delete_view(self):
        """UserDeleteView test"""
        response = self.client.post(reverse('user_del',
                                            kwargs={'pk': self.user.pk}),
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('user_list'))
        self.assertFalse(User.objects.filter(email=self.user.email).exists())

    def test_change_pass(self):
        """UserChengePass test"""
        form_data = {
            'new_password1': 'password123!#',
            'new_password2': 'password123!#',
        }
        response = self.client.post(reverse('user_changepass',
                                            kwargs={'pk': self.user.pk}),
                                    data=form_data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('main'))

    def test_group_add(self):
        """Group add test"""
        url = reverse('group_add', args=[self.user.pk, self.group.pk])
        response = self.client.get(url, follow=True)
        self.assertTrue(self.user.groups.filter(name=self.group.name).exists())
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('user_edit',
                                               kwargs={'pk': self.user.pk}))

    def test_group_del(self):
        """Group delete test"""
        self.user.groups.add(self.group)
        url = reverse('group_del', args=[self.user.pk, self.group.pk])
        response = self.client.get(url, follow=True)
        self.assertFalse(self.user.groups.filter(name=self.group.name)
                                         .exists())
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('user_edit',
                                               kwargs={'pk': self.user.pk}))
