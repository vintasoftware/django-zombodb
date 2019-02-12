==============
django-zombodb
==============

.. image:: https://badge.fury.io/py/django-zombodb.svg
    :target: https://badge.fury.io/py/django-zombodb
    :alt: PyPI Status

.. image:: https://travis-ci.org/vintasoftware/django-zombodb.svg?branch=master
    :target: https://travis-ci.org/vintasoftware/django-zombodb
    :alt: Build Status

.. image:: https://codecov.io/gh/vintasoftware/django-zombodb/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/vintasoftware/django-zombodb
    :alt: Coverage Status

.. image:: https://readthedocs.org/projects/django-zombodb/badge/?version=latest
    :target: https://django-zombodb.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

Easy Django integration with Elasticsearch through `ZomboDB <https://github.com/zombodb/zombodb>`_ Postgres Extension.
Thanks to ZomboDB, **your Django models are synced with Elasticsearch after every transaction**! Searching is also very simple: you can make
Elasticsearch queries by just calling one of the search methods on your querysets. Couldn't be easier!

Documentation
-------------

The full documentation is at `<https://django-zombodb.readthedocs.io>`_.


Quickstart
----------

1. Install ZomboDB (instructions `here <https://github.com/zombodb/zombodb/blob/master/INSTALL.md>`_)

::

    pip install django-zombodb

2. Add the `SearchQuerySet` and the `ZomboDBIndex` to your model:

.. code-block:: python

    class Restaurant(models.Model):
        name = models.TextField()

        objects = models.Manager.from_queryset(SearchQuerySet)()

        class Meta:
            indexes = [
                ZomboDBIndex(fields=[
                    'name',
                ]),
            ]

3. Make the migrations:

::

    python manage.py makemigrations

4. Add `django_zombodb.operations.ZomboDBExtension()` as the first operation of the migration you've just created:

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

5. Run the migrations (Postgres user must be SUPERUSER to create the ZomboDB extension):

::

    python manage.py migrate

6. Done! Now you can make Elasticsearch queries directly from your model:

.. code-block:: python

    Restaurant.objects.filter(is_open=True).query_string_search("brazil* AND coffee~")

Full Example
------------

Check `<https://github.com/vintasoftware/django-zombodb/tree/master/example>`_

Running Tests
-------------

You need to have Elasticsearch and Postgres instances running on default ports. Then just do:

::

    python runtests.py
