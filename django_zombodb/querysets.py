from django.db import connection, models
from django.db.models.expressions import RawSQL

from elasticsearch_dsl import Search

from django_zombodb.exceptions import InvalidElasticsearchQuery
from django_zombodb.helpers import validate_query_dict, validate_query_string
from django_zombodb.serializers import ES_JSON_SERIALIZER


class SearchQuerySetMixin:

    def annotate_score(self, attr='zombodb_score'):
        db_table = connection.ops.quote_name(self.model._meta.db_table)
        return self.annotate(**{
            attr: RawSQL('zdb.score(' + db_table + '."ctid")', [])
        })

    def order_by_score(self, score_attr='zombodb_score'):
        return self.annotate_score(score_attr).order_by('-' + score_attr, 'pk')

    def _search(self, query, query_str, validate, validate_fn, sort, score_attr, limit):
        if validate:
            is_valid = validate_fn(self.model, query)
            if not is_valid:
                raise InvalidElasticsearchQuery(
                    "Invalid Elasticsearch query: {}".format(query_str))

        if limit is not None:
            queryset = self.extra(
                where=[
                    connection.ops.quote_name(self.model._meta.db_table) + ' ==> dsl.limit(%s, %s)'
                ],
                params=[limit, query_str],
            )
        else:
            queryset = self.extra(
                where=[connection.ops.quote_name(self.model._meta.db_table) + ' ==> %s'],
                params=[query_str],
            )
        if sort:
            queryset = queryset.order_by_score(score_attr=score_attr)

        return queryset

    def query_string_search(
            self, query, validate=False, sort=False, score_attr='zombodb_score', limit=None):
        query_str = query

        return self._search(
            query=query,
            query_str=query_str,
            validate=validate,
            validate_fn=validate_query_string,
            sort=sort,
            score_attr=score_attr,
            limit=limit)

    def dict_search(
            self, query, validate=False, sort=False, score_attr='zombodb_score', limit=None):
        query_str = ES_JSON_SERIALIZER.dumps(query)

        return self._search(
            query=query,
            query_str=query_str,
            validate=validate,
            validate_fn=validate_query_dict,
            sort=sort,
            score_attr=score_attr,
            limit=limit)

    def dsl_search(
            self, query, validate=False, sort=False, score_attr='zombodb_score', limit=None):
        if isinstance(query, Search):
            raise InvalidElasticsearchQuery(
                "Do not use the `Search` class. "
                "`query` must be an instance of a class inheriting from `DslBase`.")

        query_dict = query.to_dict()

        return self.dict_search(
            query=query_dict,
            validate=validate,
            sort=sort,
            score_attr=score_attr,
            limit=limit)


class SearchQuerySet(SearchQuerySetMixin, models.QuerySet):
    pass
