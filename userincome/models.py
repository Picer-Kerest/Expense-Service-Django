from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import now


class Source(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def source_exists(self, name):
        name = name.upper()
        return Source.objects.filter(name=name).exists()

    def save(self, *args, **kwargs):
        if self.source_exists(self.name):
            raise ValidationError('Record with this name already exists')
        self.name = self.name.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Income(models.Model):
    amount = models.FloatField()
    date = models.DateField(default=now)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    source = models.CharField(max_length=255)

    def __str__(self):
        return self.source

    class Meta:
        ordering = ['-date']

