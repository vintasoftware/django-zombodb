import json

from django.contrib.admin.views.main import SEARCH_VAR
from django.db import connection
from django.db.models import IntegerField
from django.db.models.expressions import RawSQL, Value
from django.utils.http import urlencode


class ZomboDBAdminMixin:

    def _check_if_valid_search(self, request):
        search_term = request.GET.get(SEARCH_VAR, '')
        if not search_term:
            return False

        with connection.cursor() as cursor:
            q = urlencode({'q': search_term})
            cursor.execute('''
                SELECT zdb.request(
                    'deduped_entities_entitydeduped_zombo_idx',
                    %s);
            ''', ['_validate/query?' + q])
            search_validation_result = json.loads(cursor.fetchone()[0])
            return search_validation_result['valid']

    def get_list_display(self, request):
        request._has_valid_search = self._check_if_valid_search(request)
        return super().get_list_display(request)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        if getattr(request, '_has_valid_search', False):
            queryset = queryset.annotate(
                zombodb_score=RawSQL(f'zdb.score("{self.model._meta.db_table}"."ctid")', [])
            )
        else:
            queryset = queryset.annotate(zombodb_score=Value(0, IntegerField()))

        return queryset

    def get_search_results(self, request, queryset, search_term):
        if search_term:
            if request._has_valid_search:
                queryset = queryset.extra(
                    where=[f'{queryset.model._meta.db_table} ==> %s'],
                    params=[search_term],
                )
            else:
                self.message_user(
                    request,
                    "Invalid search query. Not filtering by search.",
                    level='ERROR')
        use_distinct = False
        return queryset, use_distinct

    def get_ordering(self, request):
        ordering = super().get_ordering(request)

        if getattr(request, '_has_valid_search', False):
            ordering = ('-zombodb_score', 'pk')

        return ordering

    def _zombodb_score(self, instance):
        return instance.zombodb_score
    _zombodb_score.short_description = "Search score"
    _zombodb_score.admin_order_field = 'zombodb_score'
