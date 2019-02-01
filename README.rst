=============================
django_zombodb
=============================

.. image:: https://badge.fury.io/py/django-zombodb.svg
    :target: https://badge.fury.io/py/django-zombodb

.. image:: https://travis-ci.org/fjsj/django-zombodb.svg?branch=master
    :target: https://travis-ci.org/fjsj/django-zombodb

.. image:: https://codecov.io/gh/fjsj/django-zombodb/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/fjsj/django-zombodb

Easy Django integration with ElasticSearch through ZomboDB Postgres Extension

Documentation
-------------

The full documentation is at https://django-zombodb.readthedocs.io.

Quickstart
----------

Install django_zombodb::

    pip install django-zombodb

Add it to your `INSTALLED_APPS`:

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

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
