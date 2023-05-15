from django.urls import reverse
from django.test import TestCase
from model_bakery import baker

from clients.models import Client, Contact
from users.models import User


class TestClients(TestCase):
    def setUp(self):
        self.user = baker.make(User, is_superuser=False,
                               is_staff=False, is_active=True)

    def test_client_list_view(self):
        baker.make(Client, _quantity=10)
        response = self.client.get(reverse('client_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['clients']), 10)
        self.assertTemplateUsed(response, 'clients/client_list.html')

    def test_client_create_view(self):
        response = self.client.post(reverse('client_create'), {
            'name': 'New Client',
            'web_site': 'https://example.com',
            'phone': '123456789',
            'address': '123 Main St',
            'is_active': True,
            'description': 'A new client',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Client.objects.last().name, 'New Client')

    def test_client_edit_view(self):
        client_1 = baker.make(Client)
        response = self.client.post(reverse('client_edit',
                                            args=[client_1.pk]), {
            'name': 'New Name',
            'web_site': 'https://example.com',
            'phone': '123456789',
            'address': '123 Main St',
            'is_active': True,
            'description': 'A new description',
        })
        self.assertEqual(response.status_code, 302)
        client_1.refresh_from_db()
        self.assertEqual(client_1.name, 'New Name')


class TestContacts(TestCase):
    def setUp(self):
        self.user = baker.make(User, is_superuser=False,
                               is_staff=False, is_active=True)
        self.client_1 = baker.make(Client)
        self.client_2 = baker.make(Client)
        self.contact_1 = baker.make(Contact, client_id=self.client_1.id)
        self.contact_2 = baker.make(Contact, client_id=self.client_2.id)

    def test_contact_list_view(self):
        baker.make(Contact, client_id=self.client_1.id, _quantity=5)
        response = self.client.get(reverse('contact_list',
                                           args=[self.client_1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.contact_1, response.context['contacts'])
        self.assertNotIn(self.contact_2, response.context['contacts'])
        self.assertEqual(len(response.context['contacts']), 6)

    def test_contact_create_view(self):
        response = self.client.post(reverse('contact_create',
                                            args=[self.client_1.pk]), {
            'contact': 'New Contact',
            'fio': 'New FIO',
            'description': 'A new contact',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Contact.objects.last().client_id, self.client_1.id)
        self.assertEqual(Contact.objects.last().contact, 'New Contact')

    def test_contact_edit_view(self):
        response = self.client.post(reverse('contact_edit',
                                            args=[self.client_1.pk,
                                                  self.contact_1.pk]), {
            'contact': 'New Contact',
            'fio': 'New fio'})
        self.assertEqual(response.status_code, 302)
        self.contact_1.refresh_from_db()
        self.assertEqual(self.contact_1.contact, 'New Contact')
