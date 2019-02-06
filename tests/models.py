from django.db import models
from django.contrib.postgres.fields import ArrayField


class IntegerArrayModel(models.Model):
    field = ArrayField(models.IntegerField(), default=list, blank=True)


class DateTimeArrayModel(models.Model):
    datetimes = ArrayField(models.DateTimeField())
    dates = ArrayField(models.DateField())
    times = ArrayField(models.TimeField())
