from tinymce.models import HTMLField
from django.db import models


class Client(models.Model):
    name = models.CharField(
        'Название', max_length=120, unique=True, blank=False)
    last_activity = models.DateTimeField('Последняя активность',
                                         auto_now_add=True,
                                         null=True)
    web_site = models.URLField('Сайт', max_length=200, null=True, blank=True)
    phone = models.CharField('Телефон', max_length=30, null=True, blank=True)
    address = models.CharField('Адрес', max_length=254, null=True, blank=True)
    description = HTMLField('Описание', null=True, blank=True)
    is_active = models.BooleanField('Обслуживаем', default=True)
    date_created = models.DateTimeField('Дата создания', auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = "Список клиентов"


class Contact(models.Model):
    contact = models.CharField(
        "Контакт", max_length=120, unique=True, null=False, blank=False)
    fio = models.CharField('ФИО', max_length=120, null=True, blank=True)
    description = HTMLField('Описание', null=True, blank=True)
    last_activity = models.DateTimeField('Последняя активность',
                                         auto_now_add=True,
                                         null=True)
    client = models.ForeignKey(Client,
                               null=False,
                               blank=False,
                               on_delete=models.CASCADE,
                               related_name='contact',
                               verbose_name='Клиент')

    def __str__(self):
        return self.contact

    class Meta:
        verbose_name = 'Контакты'
        verbose_name_plural = "Список контактов"
