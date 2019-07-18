==============================
Integrating with Elasticsearch
==============================

ZomboDB integrates Postgres with Elasticsearch through Postgres indexes. If you don't know much about ZomboDB, please read its `tutorial <https://github.com/zombodb/zombodb/blob/master/TUTORIAL.md>`_ before proceeding.

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

    from django_zombodb.indexes import ZomboDBIndex

    class Restaurant(models.Model):
        name = models.TextField()
        street = models.TextField()

        class Meta:
            indexes = [
                ZomboDBIndex(fields=[
                    'name',
                    'street',
                ]),
            ]

After that, create and run the migrations: ::

    python manage.py makemigrations
    python manage.py migrate

.. warning::

    During the migration, :py:class:`~django_zombodb.indexes.ZomboDBIndex` reads the value at ``settings.ZOMBODB_ELASTICSEARCH_URL``. That means if ``settings.ZOMBODB_ELASTICSEARCH_URL`` changes after the :py:class:`~django_zombodb.indexes.ZomboDBIndex` migration, **the internal index stored at Postgres will still point to the old URL**. If you wish to change the URL of an existing :py:class:`~django_zombodb.indexes.ZomboDBIndex`, change both ``settings.ZOMBODB_ELASTICSEARCH_URL`` and issue a ``ALTER INDEX index_name SET (url='http://some.new.url');`` (preferably inside a ``migrations.RunSQL`` in a new migration).

Now the ``Restaurant`` model will support Elasticsearch queries for both ``name`` and ``street`` fields. But to perform those searches, we need it to use the custom queryset :py:class:`~django_zombodb.querysets.SearchQuerySet`:

.. code-block:: python

    from django_zombodb.indexes import ZomboDBIndex
    from django_zombodb.querysets import SearchQuerySet

    class Restaurant(models.Model):
        name = models.TextField()
        street = models.TextField()

        objects = models.Manager.from_queryset(SearchQuerySet)()

        class Meta:
            indexes = [
                ZomboDBIndex(fields=[
                    'name',
                    'street',
                ]),
            ]

.. note::

    If you already have a custom queryset on your model, make it inherit from :py:class:`~django_zombodb.querysets.SearchQuerySetMixin`.

Field mapping
-------------

From `Elasticsearch documentation <https://www.elastic.co/guide/en/elasticsearch/reference/6.8/mapping.html>`_:

    "Mapping is the process of defining how a document, and the fields it contains, are stored and indexed. For instance, use mappings to define:

    - which string fields should be treated as full text fields.
    - which fields contain numbers, dates, or geolocations.
    - whether the values of all fields in the document should be indexed into the catch-all _all field.
    - the format of date values.
    - custom rules to control the mapping for dynamically added fields."

If you don't specify a mapping for your :py:class:`~django_zombodb.indexes.ZomboDBIndex`, django-zombodb uses `ZomboDB's default mappings <https://github.com/zombodb/zombodb/blob/master/TYPE-MAPPING.md#common-data-types>`_, which are based on the Postgres type of your model fields.

To customize mapping, specify a ``field_mapping`` parameter to your :py:class:`~django_zombodb.indexes.ZomboDBIndex` like below:

.. code-block:: python

    from django_zombodb.indexes import ZomboDBIndex
    from django_zombodb.querysets import SearchQuerySet

    class Restaurant(models.Model):
        name = models.TextField()
        street = models.TextField()

        objects = models.Manager.from_queryset(SearchQuerySet)()

        class Meta:
            indexes = [
                ZomboDBIndex(
                    fields=[
                        'name',
                        'street',
                    ],
                    field_mapping={
                        'name': {"type": "text",
                                 "copy_to": "zdb_all",
                                 "analyzer": "fulltext_with_shingles",
                                 "search_analyzer": "fulltext_with_shingles_search"},
                        'street': {"type": "text",
                                   "copy_to": "zdb_all",
                                   "analyzer": "brazilian"},
                    }
                )
            ]

.. note::

    You probably wish to have ``"copy_to": "zdb_all"`` on your textual fields to match ZomboDB default behavior. From ZomboDB docs: "``zdb_all`` is ZomboDB's version of Elasticsearch's "_all" field, except ``zdb_all`` is enabled for all versions of Elasticsearch. It is also configured as the default search field for every ZomboDB index". For more info, read `Elasticsearch docs take on the "_all" field <https://www.elastic.co/guide/en/elasticsearch/reference/6.8/mapping-all-field.html>`_.

Move forward to learn how to perform Elasticsearch queries through your model.
