# Generated by Django 4.1.1 on 2022-09-15 20:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0010_event_color'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='color',
        ),
    ]
