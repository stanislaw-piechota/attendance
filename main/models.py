from django.db import models
from datetime import datetime

class VerificationCode(models.Model):
    code = models.CharField(max_length=10)
    user_id = models.BigIntegerField()

    def __str__(self):
        return self.code


class Student(models.Model):
    id = models.BigIntegerField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    name = models.CharField(max_length=20)
    second_name = models.CharField(max_length=50)
    room = models.IntegerField(default=0)
    row = models.IntegerField(default=0)
    col = models.IntegerField(default=0)
    last_time = models.DateTimeField(default=datetime.now())
    class_name = models.CharField(max_length=3, default='3E')

    def __str__(self):
        return f'{self.name} {self.second_name}'


class Teacher(models.Model):
    id = models.BigIntegerField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    name = models.CharField(max_length=20, null=True)
    second_name = models.CharField(max_length=50, null=True)
    login = models.CharField(max_length=100, null=True)
    pin = models.IntegerField(null=True)
    room = models.IntegerField(null=True)
    class_name = models.CharField(max_length=3, null=True)

    def __str__(self):
        return f'{self.name} {self.second_name}'


class Seat(models.Model):
    room = models.IntegerField()
    row = models.IntegerField()
    col = models.IntegerField()
    empty = models.BooleanField()

    def __str__(self):
        return f'{self.room}, {self.row}, {self.col}'
