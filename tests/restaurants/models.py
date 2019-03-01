import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.indexes import Index

from django_zombodb.indexes import ZomboDBIndex
from django_zombodb.querysets import SearchQuerySet


class Restaurant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField()
    name = models.TextField()
    street = models.TextField()
    zip_code = models.TextField()
    city = models.TextField()
    state = models.TextField()
    phone = models.TextField()
    email = models.EmailField()
    website = models.URLField(blank=True)
    categories = ArrayField(models.TextField())

    objects = models.Manager.from_queryset(SearchQuerySet)()

    class Meta:
        indexes = [
            Index(name='other-index', fields=['url']),
            ZomboDBIndex(
                fields=[
                    'name',
                    'street',
                    'zip_code',
                    'city',
                    'state',
                    'phone',
                    'email',
                    'website',
                    'categories',
                ]
            ),
        ]

    def __str__(self):
        return self.name


class RestaurantNoIndex(models.Model):
    name = models.TextField()

    objects = models.Manager.from_queryset(SearchQuerySet)()

    def __str__(self):
        return self.name
