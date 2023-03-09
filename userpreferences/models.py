from django.db import models
from django.contrib.auth.models import User


class UserPreference(models.Model):
    """
    OneToOneField - это специальный тип поля ForeignKey,
    который используется для указания, что связь между моделями является однозначной.
    Таким образом, модель User может иметь только одного UserPreference, и наоборот.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    currency = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        user = str(self.user)
        return f'{user}s preferences'

