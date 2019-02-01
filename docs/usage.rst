=====
Usage
=====

To use django_zombodb in a project, add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_zombodb.apps.DjangoZomboDBConfig',
        ...
    )

Add django_zombodb's URL patterns:

.. code-block:: python

    from django_zombodb import urls as django_zombodb_urls


    urlpatterns = [
        ...
        url(r'^', include(django_zombodb_urls)),
        ...
    ]
