from django.db import models
from django.contrib.postgres.fields import ArrayField
from django_zombodb.indexes import ZomboDBIndex

import uuid


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

    class Meta:
        indexes = [
            ZomboDBIndex(fields=('name', 'street', 'categories')),
        ]

    def __str__(self):
        return self.name
