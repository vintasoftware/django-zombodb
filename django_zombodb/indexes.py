from django.contrib.postgres.indexes import PostgresIndex


class ZomboDBIndexStatementAdapter:
    template = "CREATE INDEX %(name)s ON %(table)s USING zombodb ((ROW(%(columns)s)::%(row_type)s)) %(extra)s"  # noqa: E501

    def __init__(self, statement, model, schema_editor, fields, row_type):
        self.statement = statement
        self.parts = self.statement.parts

        self.model = model
        self.schema_editor = schema_editor
        self.fields = fields
        self.row_type = row_type

    def references_table(self, *args, **kwargs):
        return self.statement.references_table(*args, **kwargs)

    def references_column(self, *args, **kwargs):
        return self.statement.references_column(*args, **kwargs)

    def rename_table_references(self, *args, **kwargs):
        return self.statement.rename_table_references(*args, **kwargs)

    def rename_column_references(self, *args, **kwargs):
        return self.statement.rename_column_references(*args, **kwargs)

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
        s = self.template % parts

        s = self._get_create_type() + s
        return s


class ZomboDBIndex(PostgresIndex):
    suffix = 'zombodb'

    def _get_row_type_name(self):
        # should be less than 63 (DatabaseOperations.max_name_length),
        # since Index.max_name_length is 30
        return self.name + '_row_type'

    def create_sql(self, model, schema_editor, using=''):
        statement = super().create_sql(model, schema_editor)
        with_params = self.get_with_params()
        if with_params:
            statement.parts['extra'] = 'WITH (%s) %s' % (
                ', '.join(with_params),
                statement.parts['extra'],
            )
        row_type = schema_editor.quote_name(self._get_row_type_name())
        return ZomboDBIndexStatementAdapter(
            statement, model, schema_editor, self.fields, row_type)

    def remove_sql(self, model, schema_editor):
        sql = super().remove_sql(model, schema_editor)
        row_type = schema_editor.quote_name(self._get_row_type_name())
        return sql + ('; DROP TYPE IF EXISTS %s;' % row_type)
