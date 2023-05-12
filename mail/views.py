from django.conf import settings
from django.core.files import File
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.utils import timezone
from django.template.loader import render_to_string
from email.mime.base import MIMEBase
from email import encoders

from os import getenv
import io


from mail.models import Attachment
from tasks.models import Task, Comment
from clients.models import Contact, Client


def send_mail_notice_task(task, template):
    if getenv('IMAP_SERVER'):
        template = template
        email = EmailMultiAlternatives(
            subject=task.title,
            to=[task.contacts, task.performer.email],
            headers={'References': task.mail.server_messageid,
                     'In-Reply-To': task.mail.server_messageid}
        )
        for file in task.mail.attachments.all():
            file_path = f'{settings.MEDIA_ROOT}/{file.file}'
            if not file.inline:
                email.attach_file(file_path)
            else:
                extension = str(file.file.name).split(".")[-1].lower()
                part_file = MIMEBase('image',
                                     extension,
                                     filename=file.file.name)
                part_file.add_header('Content-Id', f'<{file.file.url}>')
                part_file.set_payload(open(file_path, "rb").read())
                part_file.add_header('Content-Disposition',
                                     f'inline; filename="{file.file.name}"')
                encoders.encode_base64(part_file)
                email.attach(part_file)
                task.mail.text_html = task.mail.text_html.replace(
                    file.file.url, f'cid:{file.file.url}')

        html_message = render_to_string(template, {'task': task})
        plain_message = strip_tags(html_message)
        email.body = plain_message
        email.attach_alternative(html_message, "text/html")
        email.send()


def download_attachments(payload, filename, mail, inline=False):
    """ Download attachment files"""
    file = File(io.BytesIO(payload), name=filename)
    return Attachment.objects.create(file=file, mail=mail, inline=inline)


def create_task_from_mail(subject, text, from_email, mail):
    task = Task(title=subject,
                description=text,
                contacts=from_email,
                mail=mail)
    contact = Contact.objects.filter(contact=from_email).first()
    if contact:
        task.client = contact.client
        contact.last_activity = timezone.now()
        contact.save()
        client = Client.objects.get(id=contact.client_id)
        client.last_activity = timezone.now()
        client.save()
    task.save()
    Comment.objects.create(
        task=task, comment='<p>Задача создана автоматически<p>')
