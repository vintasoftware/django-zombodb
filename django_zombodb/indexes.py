import django
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from django_zombodb.serializers import ES_JSON_SERIALIZER


try:
    from django.contrib.postgres.indexes import PostgresIndex
except ImportError:
    # Django < 2.1
    from django_zombodb.base_indexes import PostgresIndex


class ZomboDBIndexCreateStatementAdapter:
    template = "CREATE INDEX %(name)s ON %(table)s USING zombodb ((ROW(%(columns)s)::%(row_type)s)) %(extra)s"  # noqa: E501

    def __init__(self, statement, model, schema_editor, fields, field_mapping, row_type):
        self.statement = statement
        self.parts = self.statement.parts

        self.model = model
        self.schema_editor = schema_editor
        self.fields = fields
        self.field_mapping = field_mapping
        self.row_type = row_type

    def references_table(self, *args, **kwargs):
        return self.statement.references_table(*args, **kwargs)

    def references_column(self, *args, **kwargs):
        return self.statement.references_column(*args, **kwargs)

    def rename_table_references(self, *args, **kwargs):
        return self.statement.rename_table_references(*args, **kwargs)

    def rename_column_references(self, *args, **kwargs):
        return self.statement.rename_column_references(*args, **kwargs)

    def _get_field_mapping(self):
        define_field_mapping = 'SELECT zdb.define_field_mapping(\'%s\', \'%s\', \'%s\');'
        s = ''
        if self.field_mapping:
            for field in self.field_mapping:
                mapping = ES_JSON_SERIALIZER.dumps(self.field_mapping[field])
                s += define_field_mapping % (self.parts['table'], field, mapping)
        return s

    def _get_create_type(self):
        create_type = 'CREATE TYPE %s AS (' % self.row_type
        for field in self.fields:
            field_db_type = self.model._meta.get_field(field).db_type(
                connection=self.schema_editor.connection)
            create_type += field + ' ' + field_db_type + ', '
        create_type = create_type[:-len(', ')]
        create_type += '); '
        return create_type

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, str(self))

    def __str__(self):
        parts = dict(self.parts)  # copy
        parts['row_type'] = self.row_type
        create_index = self.template % parts

        s = self._get_create_type() + self._get_field_mapping() + create_index
        return s


class ZomboDBIndexRemoveStatementAdapter:

    def __init__(self, statement, row_type):
        self.statement = statement
        self.template = self.statement.template
        self.parts = self.statement.parts

        self.row_type = row_type

    def references_table(self, *args, **kwargs):
        return self.statement.references_table(*args, **kwargs)

    def references_column(self, *args, **kwargs):
        return self.statement.references_column(*args, **kwargs)

    def rename_table_references(self, *args, **kwargs):
        return self.statement.rename_table_references(*args, **kwargs)

    def rename_column_references(self, *args, **kwargs):
        return self.statement.rename_column_references(*args, **kwargs)

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, str(self))

    def __str__(self):
        s = str(self.statement)
        s += ('; DROP TYPE IF EXISTS %s;' % self.row_type)
        return s


class ZomboDBIndex(PostgresIndex):
    suffix = 'zombodb'

    def __init__(
            self, *,
            shards=None,
            replicas=None,
            alias=None,
            refresh_interval=None,
            type_name=None,
            bulk_concurrency=None,
            batch_size=None,
            compression_level=None,
            llapi=None,
            field_mapping=None,
            **kwargs):
        url = kwargs.pop('url', None)
        if url:
            raise ImproperlyConfigured(
                "The `url` param is not supported anymore. "
                "Instead, please remove it and set ZOMBODB_ELASTICSEARCH_URL on settings.")

        try:
            url = settings.ZOMBODB_ELASTICSEARCH_URL
        except AttributeError:
            raise ImproperlyConfigured("Please set ZOMBODB_ELASTICSEARCH_URL on settings.")

        self.url = url
        self.shards = shards
        self.replicas = replicas
        self.alias = alias
        self.refresh_interval = refresh_interval
        self.type_name = type_name
        self.bulk_concurrency = bulk_concurrency
        self.batch_size = batch_size
        self.compression_level = compression_level
        self.llapi = llapi
        self.field_mapping = field_mapping
        super().__init__(**kwargs)

    def _get_row_type_name(self):
        # should be less than 63 (DatabaseOperations.max_name_length),
        # since Index.max_name_length is 30
        return self.name + '_row_type'

    def create_sql(self, model, schema_editor, using=''):  # pylint: disable=unused-argument
        statement = super().create_sql(model, schema_editor)
        row_type = schema_editor.quote_name(self._get_row_type_name())
        return ZomboDBIndexCreateStatementAdapter(
            statement, model, schema_editor, self.fields, self.field_mapping, row_type)

    def remove_sql(self, model, schema_editor):
        statement = super().remove_sql(model, schema_editor)
        row_type = schema_editor.quote_name(self._get_row_type_name())
        if django.VERSION >= (2, 2, 0):
            return ZomboDBIndexRemoveStatementAdapter(statement, row_type)
        else:
            return statement + ('; DROP TYPE IF EXISTS %s;' % row_type)

    def _get_params(self):
        return [
            ('url', self.url, str),
            ('shards', self.shards, int),
            ('replicas', self.replicas, int),
            ('alias', self.alias, str),
            ('refresh_interval', self.refresh_interval, str),
            ('type_name', self.type_name, str),
            ('bulk_concurrency', self.bulk_concurrency, int),
            ('batch_size', self.batch_size, int),
            ('compression_level', self.compression_level, int),
            ('llapi', self.llapi, bool),
            ('field_mapping', self.field_mapping, dict),
        ]

    def _format_param_value(self, value, param_type):
        if param_type == str:
            value_formatted = '"' + value + '"'
        elif param_type == int:
            value_formatted = str(value)
        else:  # param_type == bool
            value_formatted = 'true' if value else 'false'
        return value_formatted

    def deconstruct(self):
        path, args, kwargs = super().deconstruct()
        params = self._get_params()
        params = params[1:]  # don't add URL to migrations
        for param, value, __ in params:
            if value is not None:
                kwargs[param] = value
        return path, args, kwargs

    def get_with_params(self):
        with_params = []
        for param, value, param_type in self._get_params():
            if param == 'field_mapping':
                continue
            if value is not None:
                value_formatted = self._format_param_value(value, param_type)
                with_params.append('%s = %s' % (param, value_formatted))

        return with_params
