.. complexity documentation master file, created by
   sphinx-quickstart on Tue Jul  9 22:26:36 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

django-zombodb documentation
============================

Easy Django integration with ElasticSearch through `ZomboDB <https://github.com/zombodb/zombodb>`_ Postgres Extension.
Thanks to ZomboDB, your Django models are **synced in real-time** with ElasticSearch! Searching is also very simple: you can make
ElasticSearch queries by just calling the ``.search`` method on your querysets. Couldn't be easier!

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   integrating
   searching

.. toctree::
   :maxdepth: 2
   :caption: Reference

   django_zombodb

.. toctree::
   :maxdepth: 2
   :caption: Releases

   changelog

.. toctree::
   :maxdepth: 2
   :caption: Development

   contributing
   authors
