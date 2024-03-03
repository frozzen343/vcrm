from tinymce.models import HTMLField
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.mail import send_mail

from settings.models import Email
from users.models import User
from clients.models import Client
from mail.models import Mail


TASK_STATUS_CHOICES = (
    ('Новая', 'Новая'),
    ('В работе', 'В работе'),
    ('Выполнена', 'Выполнена'),
    ('Отложена', 'Отложена'),
    ('Не задача', 'Не задача'),
)


class Task(models.Model):
    title = models.CharField(
        'Заголовок', max_length=254, unique=False, blank=False)
    hours_cost = models.DecimalField('Трудозатраты в часах',
                                     max_digits=3,
                                     decimal_places=1,
                                     null=False,
                                     blank=False,
                                     default=0.5)
    status = models.CharField('Статус',
                              max_length=30,
                              null=False,
                              blank=False,
                              default='Новая',
                              choices=TASK_STATUS_CHOICES)
    description = HTMLField('Описание', null=True)
    fire = models.BooleanField('Срочная', default=False)
    drive = models.BooleanField('С выездом', default=False)
    date_created = models.DateTimeField('Дата создания', auto_now_add=True)
    date_closed = models.DateTimeField('Дата закрытия', null=True)
    created_from = models.CharField('Создано', default='vcrm',
                                    null=False, blank=False, max_length=30)
    contacts = models.CharField(
        'Контакты', max_length=90, null=True, blank=True)
    performer = models.ForeignKey(User,
                                  null=True,
                                  blank=True,
                                  on_delete=models.SET_NULL,
                                  related_name='task_performer',
                                  verbose_name='Исполнитель')

    client = models.ForeignKey(Client,
                               null=True,
                               blank=True,
                               on_delete=models.SET_NULL,
                               related_name='task_client',
                               verbose_name='Клиент')
    mail = models.ForeignKey(Mail,
                             null=True,
                             blank=True,
                             on_delete=models.SET_NULL,
                             related_name='task')

    __original_status = None

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = "Список задач"

    def __str__(self):
        return self.title

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_status = self.status

    def clean(self):
        if not self.client:
            raise ValidationError({"client": "Клиент не установлен"})

        if self.status == 'Новая' and self.performer:
            self.status = 'В работе'
            raise ValidationError(
                {"status": ("В задаче со статусом 'Новая' не может быть "
                            "исполнителя, только со статусом 'В работе'")}
            )
        if self.status == 'В работе' and not self.performer:
            self.status = 'Новая'
            raise ValidationError(
                {"status": ("В задаче со статусом 'В работе' должен быть "
                            "исполнитель задачи")}
            )
        if self.status == 'Выполнена' and not self.performer:
            self.status = 'Новая'
            raise ValidationError(
                {"status": ("В задаче со статусом 'Выполнена' должен быть "
                            "исполнитель задачи")}
            )

    def save(self, *args, **kwargs):
        if not self.pk:  # on create
            self.notify_users()
        if self.status != self.__original_status:
            if self.status == 'Выполнена':
                self.date_closed = timezone.now()
        super().save(*args, **kwargs)
        self.__original_status = self.status

    def notify_users(self):
        email = Email.objects.filter(sending=True).first()
        if email:
            users = User.objects.filter(is_active=True,
                                        notify_new_tasks=True).all()
            for user in users:
                subject = f'VCRM: Новая задача: {self.title}'
                message = ('Уведомление сформировано'
                           'и отправлено автоматически с помощью "VCRM')

                message_html = (f'{self.description}<br><br>Уведомление '
                                'сформировано и отправлено автоматически '
                                'с помощью "VCRM"')
                send_mail(subject,
                          message,
                          html_message=message_html,
                          from_email=f'{email.name} <{email.email}>',
                          recipient_list=[user.email],
                          connection=Email.get_connection())


class CommentManager(models.Manager):
    def get_user_comment_count(self):
        return self.get_queryset().filter(performer=True).count()


class Comment(models.Model):
    comment = HTMLField('Комментарий', null=False, blank=False)
    date_created = models.DateTimeField(auto_now_add=True)
    task = models.ForeignKey(Task,
                             null=True,
                             blank=True,
                             on_delete=models.CASCADE,
                             related_name='comment_task')
    performer = models.ForeignKey(User,
                                  null=True,
                                  blank=True,
                                  on_delete=models.SET_NULL,
                                  related_name='comment_performer')
    objects = CommentManager()

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = "Список комментариев"

    def __str__(self):
        return self.date_created.strftime('%m.%d.%Y %H:%M')
