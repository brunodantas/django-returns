from django.core.exceptions import ValidationError
from django.db import models

from django_returns.managers import ReturnsManager
from django_returns.models import ReturnsModel


class TestModel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    dob = models.DateField()

    objects = ReturnsManager()

    class Meta:
        app_label = "tests"


class Author(ReturnsModel):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        app_label = "tests"


class Book(ReturnsModel):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.PROTECT, related_name="books")

    class Meta:
        app_label = "tests"


class ValidatedModel(ReturnsModel):
    value = models.IntegerField()

    class Meta:
        app_label = "tests"

    def clean(self):
        if self.value < 0:
            raise ValidationError("Value cannot be negative")
