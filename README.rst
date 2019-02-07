==============
django_zombodb
==============

.. image:: https://badge.fury.io/py/django-zombodb.svg
    :target: https://badge.fury.io/py/django-zombodb

.. image:: https://travis-ci.org/vintasoftware/django-zombodb.svg?branch=master
    :target: https://travis-ci.org/vintasoftware/django-zombodb

.. image:: https://codecov.io/gh/vintasoftware/django-zombodb/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/vintasoftware/django-zombodb

Easy Django integration with ElasticSearch through `ZomboDB <https://github.com/zombodb/zombodb>`_ Postgres Extension.
Thanks to ZomboDB, your Django models are synced in real-time with ElasticSearch! More than that: you can make
ElasticSearch queries simply by calling the `.search` method on your querysets. Couldn't be easier!

Documentation
-------------

The full documentation is at `<https://django-zombodb.readthedocs.io>`_.


Quickstart
----------

Install django-zombodb: ::

    pip install django-zombodb

Add the `SearchQuerySet` and the `ZomboDBIndex` to your model:

.. code-block:: python

    class Restaurant(models.Model):
        name = models.TextField()

        objects = models.Manager.from_queryset(SearchQuerySet)()

        class Meta:
            indexes = [
                ZomboDBIndex(fields=(
                    'name',
                )),
            ]

Make the migrations: ::

    python manage.py makemigrations

Add the `django_zombodb.operations.ZomboDBExtension()` operation to the migration you've just created:

.. code-block:: python

    class Migration(migrations.Migration):

        dependencies = [
            ('restaurants', '0001_initial'),
        ]

        operations = [
            django_zombodb.operations.ZomboDBExtension(),
            ...
        ]

Run the migrations: ::

    python manage.py migrate

Now you can make ElasticSearch queries directly from your model!

.. code-block:: python

    Restaurant.objects.filter(is_open=True).search("brazil* AND coffee~")

Full Example
------------

Check `<https://github.com/vintasoftware/django-zombodb/tree/master/example>`_

Running Tests
-------------

You need to have ElasticSearch and Postgres instances running on default ports. Then just:

::

    python runtests.py
