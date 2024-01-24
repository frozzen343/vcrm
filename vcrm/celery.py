from django.core.management import call_command
from celery import Celery
from celery.schedules import crontab
from django.core.mail import EmailMessage
from os import environ, remove
import gzip
import json


environ.setdefault('DJANGO_SETTINGS_MODULE', 'vcrm.settings')

app = Celery('vcrm')
app.config_from_object('django.conf:settings')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.on_after_finalize.connect
def setup_periodic_backup(sender, **kwargs):
    # +3 hour
    sender.add_periodic_task(
        crontab(hour=3, minute=0, day_of_week='sunday'),
        make_backup.s(),
    )


@app.task
def make_backup():
    backup_path = 'backups/backup_db.json'
    compressed_file_path = f'{backup_path}.gz'

    with open(backup_path, "w") as f:
        call_command('dumpdata', '--indent=4', stdout=f)

    with open(backup_path, 'r') as file:
        data = json.load(file)

    with gzip.open(compressed_file_path, 'wb') as compressed_file:
        json_data = json.dumps(data).encode('utf-8')
        compressed_file.write(json_data)

    remove(backup_path)

    from settings.models import Email
    email = Email.objects.filter(sending=True).first()
    if email:
        message = EmailMessage(
            subject="VCRM: backup postgresql",
            body="backup postgresql",
            from_email=f'{email.name} <{email.email}>',
            to=[email.email],
            connection=Email.get_connection()
        )
        message.attach_file(compressed_file_path)
        message.send()
