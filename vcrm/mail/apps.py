from django.apps import AppConfig
from threading import Thread


class MailConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mail'

    def ready(self):
        from mail.views import mail_get
        t = Thread(target=mail_get)
        t.start()
