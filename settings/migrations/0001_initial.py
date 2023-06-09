# Generated by Django 4.2.1 on 2023-06-06 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imap', models.CharField(verbose_name='Imap server')),
                ('imap_port', models.IntegerField(verbose_name='Imap port')),
                ('smtp', models.CharField(verbose_name='Smtp server')),
                ('smtp_port', models.IntegerField(verbose_name='Smtp port')),
                ('name', models.CharField(verbose_name='Отображаемое имя')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Почта')),
                ('password', models.CharField(verbose_name='Пароль')),
                ('ssl', models.BooleanField(default=True, verbose_name='SSL')),
                ('sending', models.BooleanField(default=False, verbose_name='Рассылочная почта')),
                ('get_method', models.CharField(choices=[('manual', 'Вручную непрочитанные письма, помечая важным'), ('automatic', 'Автоматически все новые письма')], default='manual', verbose_name='Метод получения писем')),
            ],
            options={
                'verbose_name': 'Почта',
                'verbose_name_plural': 'Настройка почты',
            },
        ),
        migrations.AddConstraint(
            model_name='email',
            constraint=models.UniqueConstraint(condition=models.Q(('sending', True)), fields=('sending',), name='sending_unique'),
        ),
    ]
