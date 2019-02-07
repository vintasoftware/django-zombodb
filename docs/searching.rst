=========
Searching
=========

On models with :py:class:`~django_zombodb.indexes.ZomboDBIndex` and :py:class:`~django_zombodb.querysets.SearchQuerySet`, you can perform ElasticSearch queries. Here's how:

search method
-------------

The :py:meth:`~django_zombodb.querysets.SearchQuerySetMixin.search` method of :py:class:`~django_zombodb.querysets.SearchQuerySet`/:py:class:`~django_zombodb.querysets.SearchQuerySetMixin` supports various kinds of ElasticSearch queries:

Query string queries
~~~~~~~~~~~~~~~~~~~~

If the argument passed to the :py:meth:`~django_zombodb.querysets.SearchQuerySetMixin.search` method is a Python ``str``, it'll be interpreted as an ElasticSearch `query string <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html#query-string-syntax>`_.

.. code-block:: python

    Restaurant.objects.search("brasil~ AND steak*")

elasticsearch-dsl-py queries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Query string syntax is very limited. For supporting all kinds of ElasticSearch queries, the :py:meth:`~django_zombodb.querysets.SearchQuerySetMixin.search` method accepts arguments of `elasticsearch-dsl-py <https://elasticsearch-dsl.readthedocs.io/en/latest/search_dsl.html#queries>`_ ``Query`` objects. Those objects have the same representation power of the `ElasticSearch JSON Query DSL <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html>`_, and in fact the Python and JSON DSLs are very similar. You can do "match", "term", and even compound queries like "bool".

Here we're using the elasticsearch-dsl-py ``Q`` shortcut to create ``Query`` objects:

.. code-block:: python

    from elasticsearch_dsl import Q as ElasticSearchQ

    query = ElasticSearchQ(
        'bool',
        must=[
            ElasticSearchQ('match', name='pizza'),
            ElasticSearchQ('match', street='school')
        ]
    )
    Restaurant.objects.search(query)

dict queries
~~~~~~~~~~~~

If you pass a dict to :py:meth:`~django_zombodb.querysets.SearchQuerySetMixin.search`, it'll be processed by elasticsearch-dsl-py ``Q`` shortcut. That means if it can be converted to a valid ElasticSearch JSON, the search will succeed. Since elasticsearch-dsl-py is being used here, it's safe to pass ``date``, ``datetime``, ``Decimal``, and ``UUID`` as dict values.

.. note::

    By default, the ``validate`` parameter of the :py:meth:`~django_zombodb.querysets.SearchQuerySetMixin.search` method is ``False``. This means no ElasticSearch-side validation will be made, but you may get an :py:class:`~django_zombodb.exceptions.InvalidElasticSearchQuery` if you pass a ``dict`` query that elasticsearch-dsl-py can't understand.

Validation and Exception
~~~~~~~~~~~~~~~~~~~~~~~~

If you're receiving queries from the end-user, particularly query string queries, you should call :py:meth:`~django_zombodb.querysets.SearchQuerySetMixin.search` with ``validate=True``. This will perform ElasticSearch-side validation through the `Validate API <https://www.elastic.co/guide/en/elasticsearch/reference/current/search-validate.html>`_. When doing that, :py:class:`~django_zombodb.exceptions.InvalidElasticSearchQuery` may be raised.

.. code-block:: python

    from django_zombodb.exceptions import InvalidElasticSearchQuery

    queryset = Restaurant.objects.all()
    try:
        queryset = queryset.search("AND steak*", validate=True)
    except InvalidElasticSearchQuery:
        messages.error(request, "Invalid search query. Not filtering by search.")

Sort and score
~~~~~~~~~~~~~~

By default, the resulting queryset from :py:meth:`~django_zombodb.querysets.SearchQuerySetMixin.search` method is unordered. You can get results ordered by ElasticSearch's score passing ``sort=True``.

.. code-block:: python

    Restaurant.objects.search("brasil~ AND steak*", sort=True)

Alternatively, if you want to combine with your own ``order_by``, you can use the method :py:meth:`~django_zombodb.querysets.SearchQuerySetMixin.annotate_score`:

.. code-block:: python

    Restaurant.objects.search(
        "brazil* AND steak*"
    ).annotate_score(
        attr='zombodb_score'
    ).order_by('-zombodb_score', 'name', 'pk')

Lazy and Chainable
~~~~~~~~~~~~~~~~~~

The :py:meth:`~django_zombodb.querysets.SearchQuerySetMixin.search` method is just like a regular ``filter`` method: it returns a regular Django ``QuerySet`` that supports all operations, it's lazy, and it's chainable. Therefore, you can do things like:

.. code-block:: python

    Restaurant.objects.filter(
        name__startswith='Pizza'
    ).search(
        'name:Hut'
    ).filter(
        street__contains='Road'
    )

Limitations
~~~~~~~~~~~

Currently django-zombodb doesn't support ZomboDB's `limit, offset, sort functions <https://github.com/zombodb/zombodb/blob/master/QUERY-DSL.md#sort-and-limit-functions>`_ that work on the ElasticSearch side. Regular SQL limit/offset/order by works fine, so traditional QuerySet operations work.
