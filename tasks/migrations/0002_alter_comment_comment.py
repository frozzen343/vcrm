# Generated by Django 4.2.11 on 2024-10-15 19:55

from django.db import migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='comment',
            field=tinymce.models.HTMLField(),
        ),
    ]