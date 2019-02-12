=========
Searching
=========

On models with :py:class:`~django_zombodb.indexes.ZomboDBIndex`, use methods from :py:class:`~django_zombodb.querysets.SearchQuerySet`/:py:class:`~django_zombodb.querysets.SearchQuerySetMixin` to perform various kinds of Elasticsearch queries:

query_string_search
-------------------

The :py:meth:`~django_zombodb.querysets.SearchQuerySetMixin.query_string_search` method implements the simplest type of Elasticsearch queries: the ones with the `query string syntax <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html#query-string-syntax>`_. To use it, just pass as an argument a string that follows the query string syntax.

.. code-block:: python

    Restaurant.objects.query_string_search("brasil~ AND steak*")

dsl_search
----------

The query string syntax is user-friendly, but it's limited. For supporting all kinds of Elasticsearch queries, the recommended way is to use the :py:meth:`~django_zombodb.querysets.SearchQuerySetMixin.dsl_search` method. It accepts arguments of `elasticsearch-dsl-py <https://elasticsearch-dsl.readthedocs.io/en/latest/search_dsl.html#queries>`_ ``Query`` objects. Those objects have the same representation power of the `Elasticsearch JSON Query DSL <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html>`_. You can do "match", "term", and even compound queries like "bool".

Here we're using the elasticsearch-dsl-py ``Q`` shortcut to create ``Query`` objects:

.. code-block:: python

    from elasticsearch_dsl import Q as ElasticsearchQ

    query = ElasticsearchQ(
        'bool',
        must=[
            ElasticsearchQ('match', name='pizza'),
            ElasticsearchQ('match', street='school')
        ]
    )
    Restaurant.objects.dsl_search(query)

dict_search
-----------

If you already have a Elasticsearch JSON query mounted as a ``dict``, use the :py:meth:`~django_zombodb.querysets.SearchQuerySetMixin.dict_search` method. The ``dict`` will be serialized using the ``JSONSerializer`` of `elasticsearch-py <https://github.com/elastic/elasticsearch-py>`_, the official Python Elasticsearch client. This means dict values of ``date``, ``datetime``, ``Decimal``, and ``UUID`` types will be correctly serialized.


Validation
----------

If you're receiving queries from the end-user, particularly query string queries, you should call the search methods with ``validate=True``. This will perform Elasticsearch-side validation through the `Validate API <https://www.elastic.co/guide/en/elasticsearch/reference/current/search-validate.html>`_. When doing that, :py:class:`~django_zombodb.exceptions.InvalidElasticsearchQuery` may be raised.

.. code-block:: python

    from django_zombodb.exceptions import InvalidElasticsearchQuery

    queryset = Restaurant.objects.all()
    try:
        queryset = queryset.query_string_search("AND steak*", validate=True)
    except InvalidElasticsearchQuery:
        messages.error(request, "Invalid search query. Not filtering by search.")

Sorting by score
----------------

By default, the resulting queryset from the search methods is unordered. You can get results ordered by Elasticsearch's score passing ``sort=True``.

.. code-block:: python

    Restaurant.objects.query_string_search("brasil~ AND steak*", sort=True)

Alternatively, if you want to combine with your own ``order_by``, you can use the method :py:meth:`~django_zombodb.querysets.SearchQuerySetMixin.annotate_score`:

.. code-block:: python

    Restaurant.objects.query_string_search(
        "brazil* AND steak*"
    ).annotate_score(
        attr='zombodb_score'
    ).order_by('-zombodb_score', 'name', 'pk')

Lazy and Chainable
------------------

The search methods are like the traditional ``filter`` method: they return a regular Django ``QuerySet`` that supports all operations, and that's lazy and chainable. Therefore, you can do things like:

.. code-block:: python

    Restaurant.objects.filter(
        name__startswith='Pizza'
    ).query_string_search(
        'name:Hut'
    ).filter(
        street__contains='Road'
    )

.. warning::

    It's fine to call ``filter``/``exclude``/etc. before and after search. If possible, the best would be using only a Elasticsearch query. However, it's definitely **slow** to call search methods multiple times on the same queryset! **Please avoid this**:

    .. code-block:: python

        Restaurant.objects.query_string_search(
            'name:Pizza'
        ).query_string_search(
            'name:Hut'
        )

    While that may work as expected, it's `extremely inneficient <https://github.com/zombodb/zombodb/issues/335>`_. Instead, use compound queries like `"bool" <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-bool-query.html#query-dsl-bool-query>`_. They'll be much faster. Note that "bool" queries might be quite confusing to implement. Check tutorials about them, like `this one <https://engineering.carsguide.com.au/elasticsearch-demystifying-the-bool-query-11da737a4efb>`_.

Limitations
-----------

Currently django-zombodb doesn't support ZomboDB's `limit, offset, sort functions <https://github.com/zombodb/zombodb/blob/master/QUERY-DSL.md#sort-and-limit-functions>`_ that work on the Elasticsearch side. Regular SQL LIMIT/OFFSET/ORDER BY works fine, so traditional ``QuerySet`` operations work.
