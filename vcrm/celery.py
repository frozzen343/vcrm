from django.core.management import call_command
from celery import Celery
from celery.schedules import crontab
from django.core.mail import EmailMessage
from os import environ, getenv


environ.setdefault('DJANGO_SETTINGS_MODULE', 'vcrm.settings')

app = Celery('vcrm')
app.config_from_object('django.conf:settings')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.on_after_finalize.connect
def setup_periodic_backup(sender, **kwargs):
    # Executes every saturday morning at 4:30 a.m.
    sender.add_periodic_task(
        crontab(hour=7, minute=30, day_of_week='saturday'),
        make_backup.s(),
    )


@app.task
def make_backup():
    # call_command('loaddata', 'backups/backup_db.json')
    with open("backups/backup_db.json", "w") as f:
        call_command('dumpdata', '--indent=4', stdout=f)

    server = getenv('SMTP_SERVER')
    if server:
        email = EmailMessage(
            "VCRM: backup postgresql",
            "backup postgresql",
            None,
            [getenv('EMAIL')],
        )
        email.attach_file('backups/backup_db.json')
        email.send()
