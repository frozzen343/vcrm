from imap_tools import MailBox, AND, A

from settings.models import Email
from vcrm.celery import app
from mail.models import Mail
from mail.views import download_attachments, create_task_from_mail


@app.on_after_finalize.connect
def setup_periodic_get_mail(sender, **kwargs):
    sender.add_periodic_task(60.0, mail_get.s())


@app.task
def mail_get():
    emails = Email.objects.all()
    for email in emails:
        with MailBox(email.imap).login(email.email, email.password) as mailbox:
            get_method = AND(flagged=True, seen=False)\
                if email.get_method == 'manual' else A(new=True)

            for msg in mailbox.fetch(get_method):
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
