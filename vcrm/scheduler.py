from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from django.core.management import call_command
# from django.db import IntegrityError
from pytz import timezone
from os import remove
import json
import gzip

from django.core.mail import EmailMessage
from mail.utils import load_new_mail
from vcrm.settings import TIME_ZONE, DATABASES

# from tasks.models import Task
# from vcrm.settings import Integration
# import integrations.bitrix as b24


POSTGRESQL = (f"postgresql://{DATABASES['default']['USER']}:"
              f"{DATABASES['default']['PASSWORD']}@"
              f"{DATABASES['default']['HOST']}:"
              f"{DATABASES['default']['PORT']}/"
              f"{DATABASES['default']['NAME']}")
jobstores = {'default': SQLAlchemyJobStore(url=POSTGRESQL)}
tz = timezone(TIME_ZONE)
scheduler = BackgroundScheduler(jobstores=jobstores, timezone=tz)


# def load_bitrix_tasks():
#     """
#     Load tasks from bitrix
#     """

#     print('start load bitrix tasks')

#     data = b24.get_task_list_by_activity()
#     b24_tasks = data['result']['tasks']
#     b24_statuses = {'2': 'Новая', '3': 'В работе', '5': 'Выполнена',
#                     '6': 'Отложена'}
#     b24_ids = [b24_task['id'] for b24_task in b24_tasks]
#     vcrm_tasks = Task.objects.filter(bitrix_id__in=b24_ids)
#     vcrm_tasks_dict = {task.bitrix_id: task for task in vcrm_tasks}
#     tasks_to_create = []
#     tasks_to_update = []

#     for b24_task in b24_tasks:
#         b24_data = {
#             'bitrix_id': int(b24_task['id']),
#             'title': b24_task['title'],
#             'description': b24_task['description'],
#             'status': b24_statuses[b24_task['status']],
#             'date_created': b24_task['createdDate'],
#             'created_from': "bitrix",
#             'contacts': b24_task['creator']['name'],
#             'client_id': Integration.client_with_bitrix,
#         }

#         if b24_data['bitrix_id'] in vcrm_tasks_dict:
#             task = vcrm_tasks_dict[b24_data['bitrix_id']]
#             task.title = b24_data['title']
#             task.description = b24_data['description']
#             task.status = b24_data['status']
#             tasks_to_update.append(task)
#             # todo: notify users
#             # todo: comments
#         else:
#             if b24_data['status'] == 'Новая':
#                 tasks_to_create.append(Task(**b24_data))

#         Task.objects.bulk_create(tasks_to_create,
#                                  ignore_conflicts=True)
#         Task.objects.bulk_update(tasks_to_update, ['title', 'description',
#                                                    'status'])


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


def load_scheduler_jobs():

    # if Integration.bitrix_enabled:
    #     scheduler.add_job(load_bitrix_tasks, "interval",
    #                       id='load_bitrix_tasks',
    #                       seconds=30,
    #                       max_instances=1,
    #                       replace_existing=True)

    scheduler.add_job(make_backup, "cron",
                      id='make_backup',
                      day_of_week='sun',
                      hour=3,
                      max_instances=1,
                      replace_existing=True)

    scheduler.add_job(load_new_mail, "interval",
                      id='load_new_mail',
                      seconds=300,
                      max_instances=1,
                      replace_existing=True)
