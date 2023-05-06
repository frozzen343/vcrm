from django.conf import settings
from django.core.files import File
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from email.mime.base import MIMEBase
from email import encoders

from time import sleep
from imap_tools import MailBox, AND
from os import getenv
import io


from mail.models import Mail, Attachment
from tasks.models import Task, Comment
from clients.models import Contact


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
    task.save()
    Comment.objects.create(
        task=task, comment='<p>Задача создана автоматически<p>')


def mail_get():
    server = getenv('IMAP_SERVER')
    if not server:
        return None

    while True:
        with MailBox(server).login(settings.EMAIL_HOST_USER,
                                   settings.EMAIL_HOST_PASSWORD) as mailbox:
            # TODO: нужно? добавить автопрочтение писем new=True
            for msg in mailbox.fetch(AND(flagged=True, seen=False)):
                if not Mail.objects.filter(messageid=msg.uid):
                    text_html = msg.html
                    text_html = text_html.replace("\"", '\'')  # to Iframe work

                    mail = Mail.objects.create(
                        messageid=msg.uid,
                        from_name=msg.from_values.name,
                        from_email=msg.from_values.email,
                        to=str(*msg.to),
                        cc=str(*msg.cc),
                        date=msg.date,
                        subject=msg.subject if msg.subject else '(Без темы)',
                        text_html=text_html if text_html else msg.text,
                        server_messageid=msg.headers['message-id'][0]
                    )
                    for att in msg.attachments:
                        attachment = download_attachments(
                            att.payload, att.filename, mail=mail,
                            inline=bool(att.content_id)
                        )
                        if att.content_id:
                            text_html = text_html.replace(
                                f"cid:{att.content_id}",
                                f'{attachment.file.url}')
                            mail.text_html = text_html
                            mail.save()

                    create_task_from_mail(mail.subject,
                                          text_html,
                                          msg.from_values.email,
                                          mail)
        sleep(60)
