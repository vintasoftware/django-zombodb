# From Django 2.1, for Django < 2.1
from django.db.models import Index
from django.utils.functional import cached_property


class PostgresIndex(Index):

    @cached_property
    def max_name_length(self):
        # Allow an index name longer than 30 characters when the suffix is
        # longer than the usual 3 character limit. The 30 character limit for
        # cross-database compatibility isn't applicable to PostgreSQL-specific
        # indexes.
        return Index.max_name_length - len(Index.suffix) + len(self.suffix)

    def create_sql(self, model, schema_editor, using=''):
        statement = super().create_sql(model, schema_editor, using=' USING %s' % self.suffix)
        with_params = self.get_with_params()
        if with_params:  # pragma: no cover
            statement.parts['extra'] = 'WITH (%s) %s' % (
                ', '.join(with_params),
                statement.parts['extra'],
            )
        return statement

    def get_with_params(self):
        return []  # pragma: no cover
