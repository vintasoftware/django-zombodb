from django.db import connection, models

from django_zombodb.exceptions import InvalidElasticSearchQueryString
from django_zombodb.helpers import validate_query_string
from django.db.models.expressions import RawSQL


class SearchQuerySetMixin:

    def annotate_score(self, attr='zombodb_score'):
        db_table = connection.ops.quote_name(self.model._meta.db_table)
        return self.annotate(**{
            attr: RawSQL('zdb.score(' + db_table + '."ctid")', [])
        })

    def search(self, query, validate=True, sort=True, score_attr='zombodb_score'):
        if validate:
            is_valid = validate_query_string(self.model, query)
            if not is_valid:
                raise InvalidElasticSearchQueryString(
                    "Invalid ElasticSearch query string: {}".format(query))

        queryset = self.extra(
            where=[connection.ops.quote_name(self.model._meta.db_table) + ' ==> %s'],
            params=[query],
        ).annotate_score(score_attr)
        if sort:
            queryset = queryset.order_by('-' + score_attr, 'pk')

        return queryset


class SearchQuerySet(SearchQuerySetMixin, models.QuerySet):
    pass
