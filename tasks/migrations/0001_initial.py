# Generated by Django 4.2.11 on 2024-04-10 23:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import tinymce.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clients', '0001_initial'),
        ('mail', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=254, verbose_name='Заголовок')),
                ('hours_cost', models.DecimalField(decimal_places=1, default=0.5, max_digits=3, verbose_name='Трудозатраты в часах')),
                ('status', models.CharField(choices=[('Новая', 'Новая'), ('В работе', 'В работе'), ('Выполнена', 'Выполнена'), ('Отложена', 'Отложена'), ('Не задача', 'Не задача')], default='Новая', max_length=30, verbose_name='Статус')),
                ('description', tinymce.models.HTMLField(null=True, verbose_name='Описание')),
                ('fire', models.BooleanField(default=False, verbose_name='Срочная')),
                ('drive', models.BooleanField(default=False, verbose_name='С выездом')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('date_closed', models.DateTimeField(null=True, verbose_name='Дата закрытия')),
                ('created_from', models.CharField(default='vcrm', max_length=30, verbose_name='Создано')),
                ('contacts', models.CharField(blank=True, max_length=90, null=True, verbose_name='Контакты')),
                ('bitrix_id', models.IntegerField(blank=True, null=True, unique=True)),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='task_client', to='clients.client', verbose_name='Клиент')),
                ('mail', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='task', to='mail.mail')),
                ('performer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='task_performer', to=settings.AUTH_USER_MODEL, verbose_name='Исполнитель')),
            ],
            options={
                'verbose_name': 'Задача',
                'verbose_name_plural': 'Список задач',
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', tinymce.models.HTMLField()),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('integration_id', models.IntegerField(null=True)),
                ('comment_type', models.CharField(default='history', max_length=30)),
                ('user_name', models.CharField(max_length=100)),
                ('avatar', models.ImageField(default='default_avatar.png', upload_to='profile_images')),
                ('performer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='comment_performer', to=settings.AUTH_USER_MODEL)),
                ('task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comment_task', to='tasks.task')),
            ],
            options={
                'verbose_name': 'Комментарий',
                'verbose_name_plural': 'Список комментариев',
            },
        ),
    ]
