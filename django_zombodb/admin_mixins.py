
from django.contrib.admin.views.main import SEARCH_VAR
from django.db.models import FloatField
from django.db.models.expressions import Value
from django.utils.translation import gettext as _

from django_zombodb.helpers import validate_query_string


class ZomboDBAdminMixin:
    max_search_results = None

    def get_search_fields(self, request):
        """
        get_search_fields is unnecessary if ZomboDBAdminMixin is used.
        But since search_form.html uses this, we'll return a placeholder tuple
        """
        return ('-placeholder-',)

    def _check_if_valid_search(self, request):
        search_term = request.GET.get(SEARCH_VAR, '')
        if not search_term:
            return False

        return validate_query_string(self.model, search_term)

    def get_list_display(self, request):
        request._has_valid_search = self._check_if_valid_search(request)
        return super().get_list_display(request)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        if not getattr(request, '_has_valid_search', False):
            queryset = queryset.annotate(zombodb_score=Value(0.0, FloatField()))

        return queryset

    def get_search_results(self, request, queryset, search_term):
        if search_term:
            if request._has_valid_search:
                queryset = queryset.query_string_search(
                    search_term,
                    validate=False,
                    sort=False,
                    score_attr='zombodb_score',
                    limit=self.max_search_results
                ).annotate_score()
            else:
                self.message_user(
                    request,
                    _("Invalid search query. Not filtering by search."),
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
