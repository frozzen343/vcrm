from django.db import models
from django.db.models import Q, UniqueConstraint
from django.core.mail import get_connection


MAIL_GET_METHODS = (
    ('manual', 'Вручную непрочитанные письма, помечая важным'),
    ('automatic', 'Автоматически все новые письма'),
)


class Email(models.Model):
    imap = models.CharField('Imap server', null=False, blank=False)
    imap_port = models.IntegerField('Imap port', null=False, blank=False)
    smtp = models.CharField('Smtp server', null=False, blank=False)
    smtp_port = models.IntegerField('Smtp port', null=False, blank=False)
    name = models.CharField('Отображаемое имя', null=False, blank=False)
    email = models.EmailField('Почта', unique=True, null=False, blank=False)
    password = models.CharField('Пароль', null=False, blank=False)
    ssl = models.BooleanField('SSL', default=True)
    sending = models.BooleanField('Рассылочная почта', default=False)
    get_method = models.CharField('Метод получения писем',
                                  null=False,
                                  blank=False,
                                  default='manual',
                                  choices=MAIL_GET_METHODS)

    @staticmethod
    def get_connection():
        email = Email.objects.filter(sending=True).first()

        connection = get_connection(
            host=email.smtp,
            port=email.smtp_port,
            username=email.email,
            password=email.password,
            use_ssl=email.ssl,
        )
        return connection

    class Meta:
        constraints = [
            UniqueConstraint(
                name='sending_unique',
                condition=Q(sending=True),
                fields=['sending'],
            ),
        ]

        verbose_name = 'Почта'
        verbose_name_plural = "Настройка почты"

    def __str__(self):
        return self.email
