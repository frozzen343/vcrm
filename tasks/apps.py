from django.apps import AppConfig


class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'

    def ready(self):
        from vcrm import scheduler
        scheduler.scheduler.start()
        scheduler.load_scheduler_jobs()
