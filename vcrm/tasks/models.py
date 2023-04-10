from tinymce.models import HTMLField
from django import template
from django.db import models
from django.core.exceptions import ValidationError

from users.models import User


register = template.Library()


TASK_STATUS_CHOICES = (
    ('Новая', 'Новая'),
    ('В работе', 'В работе'),
    ('Выполнена', 'Выполнена'),
    ('Отложена', 'Отложена'),
    ('Не задача', 'Не задача'),
)


class Task(models.Model):
    # TODO:
    #     клиенты (постановщик, контакты, организация)
    #     почта
    title = models.CharField('Заголовок',
                             max_length=254,
                             unique=False,
                             blank=False)
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

    performer = models.ForeignKey(User,
                                  null=True,
                                  blank=True,
                                  on_delete=models.SET_NULL,
                                  related_name='task_performer',
                                  verbose_name='Исполнитель')

    def __str__(self):
        return self.title

    def clean(self):
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
    user_comments = CommentManager()

    def __str__(self):
        return self.performer
