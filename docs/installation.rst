==============================
Installation and Configuration
==============================

Example
-------
You can check a fully configured Django project with django-zombodb at `<https://github.com/vintasoftware/django-zombodb/tree/master/example>`_

Requirements
------------

* **Python**: 3.4, 3.5, 3.6, 3.7
* **Django**: 2.0, 2.1

Installation
------------

Install django-zombodb: ::

    pip install django-zombodb

Settings
--------

Set ``ZOMBODB_ELASTICSEARCH_URL`` on your settings.py. That is the URL of the ElasticSearch cluster used by ZomboDB.

.. code-block:: python

    ZOMBODB_ELASTICSEARCH_URL = 'http://localhost:9200/'

Move forward to learn how to integrate your models with Elasticsearch.
