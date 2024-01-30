from mail.utils import load_new_mail
from vcrm.celery import app


@app.on_after_finalize.connect
def setup_periodic_get_mail(sender, **kwargs):
    sender.add_periodic_task(300.0, mail_get.s())


@app.task
def mail_get():
    load_new_mail()
