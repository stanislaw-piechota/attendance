# Generated by Django 3.2.14 on 2022-07-14 19:33

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_auto_20220714_2127'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='class_name',
            field=models.CharField(default='3E', max_length=3),
        ),
        migrations.AlterField(
            model_name='student',
            name='last_time',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 14, 21, 33, 45, 921952)),
        ),
    ]
