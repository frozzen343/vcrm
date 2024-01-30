from django.conf import settings
from django.core.files import File
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.utils import timezone
from django.template.loader import render_to_string
from email.mime.base import MIMEBase
from email import encoders
from imap_tools import MailBox, AND, A
import io

from mail.models import Attachment, Mail
from settings.models import Email
from tasks.models import Task, Comment
from clients.models import Contact, Client


def convert_to_string(value):
    if isinstance(value, (list, tuple)):
        return ' '.join(map(str, value))
    elif isinstance(value, str):
        return value
    else:
        return str(value)


def send_mail_notice_task(task, template):
    email = Email.objects.filter(sending=True).first()
    if email:
        message = EmailMultiAlternatives(
            subject=task.title,
            from_email=f'{email.name} <{email.email}>',
            to=[task.contacts, task.performer.email],
            headers={'References': task.mail.server_messageid,
                     'In-Reply-To': task.mail.server_messageid},
            connection=Email.get_connection()
        )

        for file in task.mail.attachments.all():
            file_path = f'{settings.MEDIA_ROOT}/{file.file}'
            if not file.inline:
                message.attach_file(file_path)
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
                message.attach(part_file)
                task.mail.text_html = task.mail.text_html.replace(
                    file.file.url, f'cid:{file.file.url}')

        html_message = render_to_string(template, {'task': task})
        plain_message = strip_tags(html_message)
        message.body = plain_message
        message.attach_alternative(html_message, "text/html")
        message.send()


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


def load_new_mail():
    """
    Download mail from added emails
    """
    emails = Email.objects.all()
    if len(emails) == 0:
        return 'Почта ещё не настроена'
    mail_count = 0
    for email in emails:
        with MailBox(email.imap).login(email.email, email.password) as mailbox:
            get_method = AND(flagged=True, seen=False)\
                if email.get_method == 'manual' else A(new=True)

            for msg in mailbox.fetch(get_method):
                if not Mail.objects.filter(messageid=msg.uid):
                    text_html = msg.html
                    text_html = text_html.replace("\"", '\'')  # to Iframe work
                    msg_to = convert_to_string(msg.to)
                    msg_cc = convert_to_string(msg.cc)

                    mail = Mail.objects.create(
                        messageid=msg.uid,
                        from_name=msg.from_values.name,
                        from_email=msg.from_values.email,
                        to=msg_to,
                        cc=msg_cc,
                        date=msg.date,
                        subject=msg.subject if msg.subject else '(Без темы)',
                        text_html=text_html if text_html else msg.text,
                        server_messageid=msg.headers['message-id'][0]
                    )
                    for att in msg.attachments:
                        attachment = download_attachments(
                            att.payload, att.filename or 'no_name', mail=mail,
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
                    mail_count += 1
    return f'Загружено новых писем: {mail_count}'
