# Generated by Django 3.2.14 on 2022-07-21 10:06

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_auto_20220719_2348'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='last_time',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 21, 10, 6, 31, 597964)),
        ),
        migrations.AlterField(
            model_name='teacher',
            name='class_name',
            field=models.CharField(default='NO', max_length=3, null=True),
        ),
        migrations.AlterField(
            model_name='teacher',
            name='last_activity',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 21, 10, 6, 31, 597964)),
        ),
        migrations.AlterField(
            model_name='teacher',
            name='room',
            field=models.IntegerField(default=0, null=True),
        ),
    ]