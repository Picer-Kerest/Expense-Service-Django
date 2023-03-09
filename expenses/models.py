from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import now
# С учётом даты и времени
# current_time = now()
# print("Текущее время:", current_time.strftime("%d.%m.%Y %H:%M:%S"))
# метод strftime() для форматирования объекта datetime.datetime в строку с заданным форматом.


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def category_exists(self, name):
        name = name.upper()
        return Category.objects.filter(name=name).exists()

    def save(self, *args, **kwargs):
        if self.category_exists(self.name):
            raise ValidationError('Record with this name already exists')
        self.name = self.name.upper()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Expense(models.Model):
    # Table Name for PostgreSQL: expenses_expense
    amount = models.FloatField()
    date = models.DateField(default=now)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    # category = models.ForeignKey(Category, on_delete=models.CASCADE)
    category = models.CharField(max_length=255)

    def __str__(self):
        return self.description

    class Meta:
        ordering = ['-date']

        