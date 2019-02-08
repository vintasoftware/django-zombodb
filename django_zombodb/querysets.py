from django.db import connection, models
from django.db.models.expressions import RawSQL

from elasticsearch_dsl import Search

from django_zombodb.exceptions import InvalidElasticsearchQuery
from django_zombodb.helpers import json_serializer, validate_query_dict, validate_query_string


class SearchQuerySetMixin:

    def annotate_score(self, attr='zombodb_score'):
        db_table = connection.ops.quote_name(self.model._meta.db_table)
        return self.annotate(**{
            attr: RawSQL('zdb.score(' + db_table + '."ctid")', [])
        })

    def order_by_score(self, score_attr='zombodb_score'):
        return self.annotate_score(score_attr).order_by('-' + score_attr, 'pk')

    def _search(self, query, query_str, validate, validate_fn, sort, score_attr):
        if validate:
            is_valid = validate_fn(self.model, query)
            if not is_valid:
                raise InvalidElasticsearchQuery(
                    "Invalid Elasticsearch query: {}".format(query_str))

        queryset = self.extra(
            where=[connection.ops.quote_name(self.model._meta.db_table) + ' ==> %s'],
            params=[query_str],
        )
        if sort:
            queryset = queryset.order_by_score(score_attr=score_attr)

        return queryset

    def query_string_search(self, query, validate=False, sort=False, score_attr='zombodb_score'):
        query_str = query

        return self._search(
            query=query,
            query_str=query_str,
            validate=validate,
            validate_fn=validate_query_string,
            sort=sort,
            score_attr=score_attr)

    def dict_search(self, query, validate=False, sort=False, score_attr='zombodb_score'):
        query_str = json_serializer.dumps(query)

        return self._search(
            query=query,
            query_str=query_str,
            validate=validate,
            validate_fn=validate_query_dict,
            sort=sort,
            score_attr=score_attr)

    def dsl_search(self, query, validate=False, sort=False, score_attr='zombodb_score'):
        if isinstance(query, Search):
            raise InvalidElasticsearchQuery(
                "Do not use the `Search` class. "
                "`query` must be an instance of a class inheriting from `DslBase`.")

        query_dict = query.to_dict()

        return self.dict_search(
            query=query_dict,
            validate=validate,
            sort=sort,
            score_attr=score_attr)


class SearchQuerySet(SearchQuerySetMixin, models.QuerySet):
    pass
