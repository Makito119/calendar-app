# Generated by Django 4.1.1 on 2022-09-15 19:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0009_alter_event_end_date_alter_event_start_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='color',
            field=models.CharField(default='#257e4a', max_length=100),
            preserve_default=False,
        ),
    ]
