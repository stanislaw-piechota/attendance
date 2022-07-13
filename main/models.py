from django.db import models


class VerificationCode(models.Model):
    code = models.CharField(max_length=10)
    user_id = models.BigIntegerField()

    def __str__(self):
        return self.code


class Studnet(models.Model):
    id = models.BigIntegerField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    name = models.CharField(max_length=20)
    second_name = models.CharField(max_length=50)
    room = models.IntegerField(default=0)
    row = models.IntegerField(default=0)
    col = models.IntegerField(default=0)
    photo = models.ImageField(upload_to='images/', default=None)


class Teacher(models.Model):
    pass
