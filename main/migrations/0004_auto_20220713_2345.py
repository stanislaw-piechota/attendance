# Generated by Django 3.2.14 on 2022-07-13 21:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20220713_2343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studnet',
            name='col',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='studnet',
            name='room',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='studnet',
            name='row',
            field=models.IntegerField(default=0),
        ),
    ]
