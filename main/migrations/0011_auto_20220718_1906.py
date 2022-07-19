# Generated by Django 3.2.14 on 2022-07-18 17:06

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_auto_20220714_2135'),
    ]

    operations = [
        migrations.CreateModel(
            name='Seat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room', models.IntegerField()),
                ('row', models.IntegerField()),
                ('col', models.IntegerField()),
                ('empty', models.BooleanField()),
            ],
        ),
        migrations.AlterField(
            model_name='student',
            name='last_time',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 18, 19, 6, 52, 5199)),
        ),
    ]
