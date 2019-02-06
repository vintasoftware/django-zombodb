from django.db import migrations

from django_zombodb.operations import ZomboDBExtension


class Migration(migrations.Migration):

    operations = [
        ZomboDBExtension(),
    ]
