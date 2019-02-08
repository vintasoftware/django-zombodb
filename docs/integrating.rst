==============================
Integrating with Elasticsearch
==============================

ZomboDB integrates Postgres with Elasticsearch through Postgres indexes. You can learn more about how ZomboDB works by reading its `tutorial <https://github.com/zombodb/zombodb/blob/master/TUTORIAL.md>`_, but you don't need that to proceed. Just know that the integration is possible due to indexes and that ZomboDB is a Postgres extension.

Installing ZomboDB extension
----------------------------

Since ZomboDB is a Postgres extension, you must install and activate it. Follow the official ZomboDB installation `instructions <https://github.com/zombodb/zombodb/blob/master/INSTALL.md>`_.

Activating ZomboDB extension
----------------------------

django-zombodb provides a Django migration operation to activate ZomboDB extension on your database. To run it, please make sure your database user is a superuser: ::

    psql -d your_database -c "ALTER USER your_database_user SUPERUSER"

Then create an empty migration on your "main" app (usually called "core" or "common"): ::

    python manage.py makemigrations core --empty

Add the :py:class:`django_zombodb.operations.ZomboDBExtension` operation to the migration you've just created:

.. code-block:: python

    import django_zombodb.operations

    class Migration(migrations.Migration):

        dependencies = [
            ('restaurants', '0001_initial'),
        ]

        operations = [
            django_zombodb.operations.ZomboDBExtension(),
            ...
        ]

Alternatively, you can activate the extension manually with a command. But you should **avoid** this because you'll need to remember to run this on production, on tests, and on the machines of all your co-workers: ::

     psql -d django_zombodb -c "CREATE EXTENSION zombodb"

Creating an index
-----------------

Imagine you have the following model:

.. code-block:: python

    class Restaurant(models.Model):
        name = models.TextField()
        street = models.TextField()

To integrate it with Elasticsearch, we need to add a :py:class:`~django_zombodb.indexes.ZomboDBIndex` to it:

.. code-block:: python

    class Restaurant(models.Model):
        name = models.TextField()
        street = models.TextField()

        class Meta:
            indexes = [
                ZomboDBIndex(fields=(
                    'name',
                    'street',
                )),
            ]

Now that model will support Elasticsearch queries for both ``name`` and ``street`` fields. But to perform those searches, we need it to use the custom queryset :py:class:`~django_zombodb.querysets.SearchQuerySet`:

.. code-block:: python

    class Restaurant(models.Model):
        name = models.TextField()
        street = models.TextField()

        objects = models.Manager.from_queryset(SearchQuerySet)()

        class Meta:
            indexes = [
                ZomboDBIndex(fields=(
                    'name',
                    'street',
                )),
            ]

.. note::

    If you already have a custom queryset on your model, make it inherit from :py:class:`~django_zombodb.querysets.SearchQuerySetMixin`.

Move forward to learn how to perform Elasticsearch queries through your model.
