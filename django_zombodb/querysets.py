from django.db import connection, models
from django.db.models.expressions import RawSQL

from elasticsearch.serializer import JSONSerializer
from elasticsearch_dsl import Search
from elasticsearch_dsl.exceptions import UnknownDslObject
from elasticsearch_dsl.query import Q as ElasticSearchQ

from django_zombodb.exceptions import InvalidElasticSearchQuery
from django_zombodb.helpers import validate_query


class SearchQuerySetMixin:

    def annotate_score(self, attr='zombodb_score'):
        db_table = connection.ops.quote_name(self.model._meta.db_table)
        return self.annotate(**{
            attr: RawSQL('zdb.score(' + db_table + '."ctid")', [])
        })

    def order_by_score(self, score_attr='zombodb_score'):
        return self.annotate_score(score_attr).order_by('-' + score_attr, 'pk')

    def search(self, query, validate=False, sort=False, score_attr='zombodb_score'):
        if isinstance(query, Search):
            raise InvalidElasticSearchQuery(
                "Do not use the `Search` class. "
                "`query` must be a query string str, a dict or an instance of "
                "a class inheriting from `DslBase`.")
        elif not isinstance(query, str):
            try:
                query_dict = ElasticSearchQ(query).to_dict()
                query = JSONSerializer().dumps(query_dict)
            except UnknownDslObject:
                raise InvalidElasticSearchQuery(
                    "Don't know how to handle DSL: {}".format(query))
        else:  # str
            query_dict = None

        if validate:
            is_valid = validate_query(self.model, query_dict or query)
            if not is_valid:
                raise InvalidElasticSearchQuery(
                    "Invalid ElasticSearch query: {}".format(query))

        queryset = self.extra(
            where=[connection.ops.quote_name(self.model._meta.db_table) + ' ==> %s'],
            params=[query],
        )
        if sort:
            queryset = queryset.order_by_score(score_attr=score_attr)

        return queryset


class SearchQuerySet(SearchQuerySetMixin, models.QuerySet):
    pass
