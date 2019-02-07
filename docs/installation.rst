==============================
Installation and Configuration
==============================

Example
-------
You can check a fully configured Django project with django-zombodb at `<https://github.com/vintasoftware/django-zombodb/tree/master/example>`_

Installation
------------

Install django-zombodb: ::

    pip install django-zombodb

Settings
--------

Set ``ZOMBODB_ELASTICSEARCH_URL`` on your settings.py. That will be the default URL set on your ZomboDB indexes.

.. code-block:: python

    ZOMBODB_ELASTICSEARCH_URL = 'http://localhost:9200/'

Move forward to learn how to integrate your models with ElasticSearch.
