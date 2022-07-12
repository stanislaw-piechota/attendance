from django.db import models


class VerificationCode(models.Model):
    code = models.CharField(max_length=10)

    def __str__(self):
        return self.code
