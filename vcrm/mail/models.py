from django.db import models


class Mail(models.Model):
    messageid = models.IntegerField('id', unique=True, null=False)
    from_name = models.CharField('Имя', max_length=255, null=True)
    from_email = models.EmailField('Почта', null=False)
    to = models.CharField('Кому', max_length=255, null=True)
    cc = models.CharField('Копия', max_length=255, null=True)
    date = models.DateField('Дата', null=False)
    subject = models.CharField(
        'Тема', max_length=255, null=False, default='(Без темы)')
    text_html = models.TextField('Текст', null=True)
    server_messageid = models.CharField(max_length=255, null=False)

    def __str__(self):
        return self.subject


class Attachment(models.Model):
    file = models.ImageField("Вложение", null=False, upload_to='mail_media')
    inline = models.BooleanField('В письме', null=False, default=False)
    mail = models.ForeignKey(Mail,
                             null=True,
                             on_delete=models.CASCADE,
                             related_name='attachments')

    def __str__(self):
        return self.file
