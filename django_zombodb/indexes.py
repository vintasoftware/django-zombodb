from django.contrib.postgres.indexes import PostgresIndex


class ZomboDBIndexStatementAdapter:

    def __init__(self, statement, model, schema_editor, fields):
        self.statement = statement
        self.template = self.statement.template
        self.parts = self.statement.parts

        self.model = model
        self.schema_editor = schema_editor
        self.fields = fields
        max_name_length = self.schema_editor.connection.ops.max_name_length()
        self.idx_type = (
            self.model._meta.db_table[:max_name_length - len('_idx_type')] +
            '_idx_type')

        statement.parts['using'] = self._get_using()

    def references_table(self, *args, **kwargs):
        return self.statement.references_table(*args, **kwargs)

    def references_column(self, *args, **kwargs):
        return self.statement.references_column(*args, **kwargs)

    def rename_table_references(self, *args, **kwargs):
        raise NotImplementedError

    def rename_column_references(self, *args, **kwargs):
        raise NotImplementedError

    def _get_using(self):
        suffix = ' USING zombodb '
        if list(self.fields) == ['*']:
            suffix += '((table_name.*))'
        else:
            suffix += '((ROW('
            for field in self.fields:
                suffix += field + ', '
            suffix = suffix[:-len(', ')]
            suffix += ')::%s));' % self.idx_type
        return suffix

    def _get_create_type(self):
        create_type = 'CREATE TYPE %s AS (' % self.idx_type
        for field in self.fields:
            field_db_type = self.model._meta.get_field(field).db_type(
                connection=self.schema_editor.connection)
            create_type += field + ' ' + field_db_type + ', '
        create_type = create_type[:-len(', ')]
        create_type += '); '
        return create_type

    def __str__(self):
        parts = dict(self.parts)
        parts['columns'] = ''
        s = self.template % parts
        s = s.replace('()', '')
        s = self._get_create_type() + s
        return s


class ZomboDBIndex(PostgresIndex):

    def __init__(self, *, fields=(), **kwargs):
        if not isinstance(fields, (list, tuple)) or not fields:
            raise ValueError(
                "fields must be a list/tuple with a single '*' "
                "or a list/tuple of field names")
        super().__init__(fields=fields, **kwargs)

    def deconstruct(self):
        path, args, kwargs = super().deconstruct()
        kwargs['fields'] = self.fields
        return path, args, kwargs

    def create_sql(self, model, schema_editor, using=''):
        # no using, see ZomboDBIndexStatementAdapter
        statement = super().create_sql(model, schema_editor)
        with_params = self.get_with_params()
        if with_params:
            statement.parts['extra'] = 'WITH (%s) %s' % (
                ', '.join(with_params),
                statement.parts['extra'],
            )
        return ZomboDBIndexStatementAdapter(
            statement, model, schema_editor, self.fields)
