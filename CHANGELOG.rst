.. :changelog:

Change Log
----------

0.3.0 (2019-07-18)
++++++++++++++++++

* Support for custom Elasticsearch mappings through ``field_mapping`` parameter on ``ZomboDBIndex``.
* Support to ``limit`` parameter on search methods.

0.2.1 (2019-06-13)
++++++++++++++++++

* Dropped support for Python 3.4.
* Added missing imports to docs.


0.2.0 (2019-03-01)
++++++++++++++++++

* Removed parameter ``url`` from ``ZomboDBIndex``. This simplifies the support of multiple deployment environments (local, staging, production), because the ElasticSearch URL isn't copied to inside migrations code (see `Issue #17 <https://github.com/vintasoftware/django-zombodb/issues/17>`_).


0.1.0 (2019-02-01)
++++++++++++++++++

* First release on PyPI.
