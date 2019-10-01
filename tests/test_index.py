from collections import OrderedDict

import django
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import connection
from django.test import TestCase, override_settings

from django_zombodb.indexes import ZomboDBIndex

from .models import DateTimeArrayModel, IntegerArrayModel


@override_settings(ZOMBODB_ELASTICSEARCH_URL='http://localhost:9999/')
class ZomboDBIndexCreateStatementAdapterTests(TestCase):
    maxDiff = 10000

    def setUp(self):
        self.index_name = 'my_test_index'
        self.index = ZomboDBIndex(
            fields=['datetimes', 'dates', 'times'],
            field_mapping=OrderedDict([  # use OrderedDict to stabilize tests on Python < 3.6
                ('datetimes', OrderedDict(
                    [('type', 'date'), ('format', 'HH:mm:ss.SSSSSS'), ('copy_to', 'zdb_all')])),
                ('dates', OrderedDict([('type', 'date'), ('copy_to', 'zdb_all')])),
                ('times', OrderedDict([('type', 'date'), ('copy_to', 'zdb_all')])),
            ]),
            name=self.index_name,
            shards=4,
            replicas=1,
            alias='my-test-index-alias',
            refresh_interval='1s',
            type_name='doc',
            bulk_concurrency=10,
            batch_size=8388608,
            compression_level=9,
            llapi=False,
        )
        with connection.schema_editor() as editor:
            self.statement_adapter = self.index.create_sql(
                model=DateTimeArrayModel,
                schema_editor=editor,
                using='')
            self.repr = repr(self.statement_adapter)
            self.str = str(self.statement_adapter)

    def test_references_table(self):
        self.assertIs(
            self.statement_adapter.references_table(DateTimeArrayModel._meta.db_table), True)
        self.assertIs(
            self.statement_adapter.references_table(IntegerArrayModel._meta.db_table), False)

    def test_references_column(self):
        self.assertIs(
            self.statement_adapter.references_column(
                DateTimeArrayModel._meta.db_table,
                'datetimes'
            ), True)
        self.assertIs(
            self.statement_adapter.references_column(
                DateTimeArrayModel._meta.db_table,
                'other'
            ), False)

    def test_rename_table_references(self):
        self.statement_adapter.rename_table_references(
            DateTimeArrayModel._meta.db_table,
            'other')
        self.assertEqual(
            repr(self.statement_adapter.parts['table']),
            '<Table \'"other"\'>')

    def test_rename_column_references(self):
        self.statement_adapter.rename_column_references(
            DateTimeArrayModel._meta.db_table,
            'dates',
            'other')
        self.assertEqual(
            repr(self.statement_adapter.parts['columns']),
            '<Columns \'"datetimes", "other", "times"\'>')

    def test_repr(self):
        self.assertEqual(
            self.repr,
            '<ZomboDBIndexCreateStatementAdapter \'CREATE TYPE "my_test_index_row_type" AS '
            '(datetimes timestamp with time zone[], dates date[], times time[]); '
            'SELECT zdb.define_field_mapping(\\\'"tests_datetimearraymodel"\\\', \\\'datetimes\\\', '  # noqa: E501
            '\\\'{"type":"date","format":"HH:mm:ss.SSSSSS","copy_to":"zdb_all"}\\\');'
            'SELECT zdb.define_field_mapping(\\\'"tests_datetimearraymodel"\\\', \\\'dates\\\', '
            '\\\'{"type":"date","copy_to":"zdb_all"}\\\');'
            'SELECT zdb.define_field_mapping(\\\'"tests_datetimearraymodel"\\\', \\\'times\\\', '
            '\\\'{"type":"date","copy_to":"zdb_all"}\\\');'
            'CREATE INDEX "my_test_index" ON "tests_datetimearraymodel" '
            'USING zombodb ((ROW("datetimes", "dates", "times")::"my_test_index_row_type")) '
            'WITH (url = \\\'http://localhost:9999/\\\', shards = 4, replicas = 1, '
            'alias = \\\'my-test-index-alias\\\', refresh_interval = \\\'1s\\\', type_name = \\\'doc\\\', '  # noqa: E501
            'bulk_concurrency = 10, batch_size = 8388608, compression_level = 9, llapi = false) \'>'
        )

    def test_str(self):
        self.assertEqual(
            self.str,
            'CREATE TYPE "my_test_index_row_type" '
            'AS (datetimes timestamp with time zone[], dates date[], times time[]); '
            'SELECT zdb.define_field_mapping(\'"tests_datetimearraymodel"\', \'datetimes\', '
            '\'{"type":"date","format":"HH:mm:ss.SSSSSS","copy_to":"zdb_all"}\');'
            'SELECT zdb.define_field_mapping(\'"tests_datetimearraymodel"\', \'dates\', '
            '\'{"type":"date","copy_to":"zdb_all"}\');'
            'SELECT zdb.define_field_mapping(\'"tests_datetimearraymodel"\', \'times\', '
            '\'{"type":"date","copy_to":"zdb_all"}\');'
            'CREATE INDEX "my_test_index" ON "tests_datetimearraymodel" '
            'USING zombodb ((ROW("datetimes", "dates", "times")::"my_test_index_row_type")) '
            'WITH (url = \'http://localhost:9999/\', shards = 4, replicas = 1, '
            'alias = \'my-test-index-alias\', refresh_interval = \'1s\', type_name = \'doc\', '
            'bulk_concurrency = 10, batch_size = 8388608, compression_level = 9, llapi = false) '
        )


@override_settings(ZOMBODB_ELASTICSEARCH_URL='http://localhost:9999')
class ZomboDBIndexRemoveStatementAdapter(TestCase):

    def setUp(self):
        self.index_name = 'my_other_test_index'
        self.index = ZomboDBIndex(
            fields=['dates', 'times'],
            name=self.index_name,
        )
        with connection.schema_editor() as editor:
            self.statement_adapter_or_str = self.index.remove_sql(
                model=DateTimeArrayModel,
                schema_editor=editor)
            self.str = str(self.statement_adapter_or_str)
            self.repr = repr(self.statement_adapter_or_str)

    def test_references_table(self):
        if django.VERSION >= (2, 2, 0):
            self.assertIs(
                self.statement_adapter_or_str.references_table(
                    DateTimeArrayModel._meta.db_table), True)
            self.assertIs(
                self.statement_adapter_or_str.references_table(
                    IntegerArrayModel._meta.db_table), False)

    def test_references_column(self):
        if django.VERSION >= (2, 2, 0):
            self.assertIs(
                self.statement_adapter_or_str.references_column(  # does nothing
                    DateTimeArrayModel._meta.db_table,
                    'dates'
                ), False)
            self.assertNotIn('columns', self.statement_adapter_or_str.parts)

    def test_rename_table_references(self):
        if django.VERSION >= (2, 2, 0):
            self.statement_adapter_or_str.rename_table_references(
                DateTimeArrayModel._meta.db_table,
                'other')
            self.assertEqual(
                repr(self.statement_adapter_or_str.parts['table']),
                '<Table \'"other"\'>')

    def test_rename_column_references(self):
        if django.VERSION >= (2, 2, 0):
            self.statement_adapter_or_str.rename_column_references(  # does nothing
                DateTimeArrayModel._meta.db_table,
                'dates',
                'other')
            self.assertNotIn('columns', self.statement_adapter_or_str.parts)

    def test_repr(self):
        if django.VERSION >= (2, 2, 0):
            self.assertEqual(
                self.repr,
                '<ZomboDBIndexRemoveStatementAdapter '
                '\'DROP INDEX IF EXISTS "my_other_test_index"; '
                'DROP TYPE IF EXISTS "my_other_test_index_row_type";\'>'
            )

    def test_str(self):
        self.assertEqual(
            self.str,
            'DROP INDEX IF EXISTS "my_other_test_index"; '
            'DROP TYPE IF EXISTS "my_other_test_index_row_type";')


# Based on django/tests/postgres_tests/test_indexes.py
@override_settings(ZOMBODB_ELASTICSEARCH_URL='http://localhost:9999')
class ZomboDBIndexTests(TestCase):

    def test_suffix(self):
        self.assertEqual(ZomboDBIndex.suffix, 'zombodb')

    def test_eq(self):
        index = ZomboDBIndex(fields=['title'])
        same_index = ZomboDBIndex(fields=['title'])
        another_index = ZomboDBIndex(fields=['author'])
        self.assertEqual(index, same_index)
        self.assertNotEqual(index, another_index)

    def test_name_auto_generation(self):
        index = ZomboDBIndex(fields=['datetimes', 'dates', 'times'])
        index.set_name_with_model(DateTimeArrayModel)
        self.assertEqual(index.name, 'tests_datet_datetim_22445c_zombodb')

    def test_deconstruction(self):
        index = ZomboDBIndex(
            fields=['title'],
            field_mapping=OrderedDict([('title', {'type': 'text'})]),
            name='test_title_zombodb',
            shards=2,
            replicas=2,
            alias='test-alias',
            refresh_interval='10s',
            type_name='test-doc',
            bulk_concurrency=20,
            batch_size=8388608 * 2,
            compression_level=9,
            llapi=True,
        )
        path, args, kwargs = index.deconstruct()
        self.assertEqual(path, 'django_zombodb.indexes.ZomboDBIndex')
        self.assertEqual(args, ())
        self.assertEqual(
            kwargs,
            {
                'fields': ['title'],
                'field_mapping': OrderedDict([('title', {'type': 'text'})]),
                'name': 'test_title_zombodb',
                'shards': 2,
                'replicas': 2,
                'alias': 'test-alias',
                'refresh_interval': '10s',
                'type_name': 'test-doc',
                'bulk_concurrency': 20,
                'batch_size': 8388608 * 2,
                'compression_level': 9,
                'llapi': True,
            }
        )

    def test_deconstruct_no_args(self):
        index = ZomboDBIndex(fields=['title'], name='test_title_zombodb')
        path, args, kwargs = index.deconstruct()
        self.assertEqual(path, 'django_zombodb.indexes.ZomboDBIndex')
        self.assertEqual(args, ())
        self.assertEqual(
            kwargs,
            {
                'fields': ['title'],
                'name': 'test_title_zombodb'
            }
        )


class ZomboDBIndexURLTests(TestCase):

    @override_settings()
    def test_exception_no_url(self):
        del settings.ZOMBODB_ELASTICSEARCH_URL

        with self.assertRaises(ImproperlyConfigured) as cm:
            ZomboDBIndex(fields=['title'], name='test_title_zombodb')

        self.assertEqual(
            str(cm.exception),
            "Please set ZOMBODB_ELASTICSEARCH_URL on settings.")

    def test_exception_old_url_param(self):
        with self.assertRaises(ImproperlyConfigured) as cm:
            ZomboDBIndex(url='http://localhost:9200/', fields=['title'], name='test_title_zombodb')

        self.assertEqual(
            str(cm.exception),
            "The `url` param is not supported anymore. "
            "Instead, please remove it and set ZOMBODB_ELASTICSEARCH_URL on settings.")


# Based on django/tests/postgres_tests/test_indexes.py
@override_settings(ZOMBODB_ELASTICSEARCH_URL='http://localhost:9200/')
class ZomboDBIndexSchemaTests(TestCase):
    '''
    This test needs a running Elasticsearch instance at http://localhost:9200/
    '''

    def get_constraints(self, table):
        """
        Get the indexes on the table using a new cursor.
        """
        with connection.cursor() as cursor:
            return connection.introspection.get_constraints(cursor, table)

    def test_zombodb_index(self):
        # Ensure the table is there and doesn't have an index.
        self.assertNotIn('field', self.get_constraints(IntegerArrayModel._meta.db_table))
        # Add the index
        index_name = 'integer_array_model_field_zombodb'
        index = ZomboDBIndex(fields=['field'], name=index_name)
        with connection.schema_editor() as editor:
            editor.add_index(IntegerArrayModel, index)
        constraints = self.get_constraints(IntegerArrayModel._meta.db_table)
        # Check zombodb index was added
        self.assertEqual(constraints[index_name]['type'], ZomboDBIndex.suffix)
        # Drop the index
        with connection.schema_editor() as editor:
            editor.remove_index(IntegerArrayModel, index)
        self.assertNotIn(index_name, self.get_constraints(IntegerArrayModel._meta.db_table))

    def test_zombodb_parameters(self):
        index_name = 'integer_array_zombodb_params'
        index = ZomboDBIndex(
            fields=['field'],
            field_mapping=OrderedDict([('title', {'type': 'text'})]),
            name=index_name,
            shards=2,
            replicas=2,
            alias='test-alias',
            refresh_interval='10s',
            type_name='test-doc',
            bulk_concurrency=20,
            batch_size=8388608 * 2,
            compression_level=9,
            llapi=True,
        )
        with connection.schema_editor() as editor:
            editor.add_index(IntegerArrayModel, index)
        constraints = self.get_constraints(IntegerArrayModel._meta.db_table)
        self.assertEqual(constraints[index_name]['type'], ZomboDBIndex.suffix)
        actual_options = constraints[index_name]['options']
        for expected_option in [
            "url=http://localhost:9200/",
            "shards=2",
            "replicas=2",
            "alias=test-alias",
            "refresh_interval=10s",
            "type_name=test-doc",
            "bulk_concurrency=20",
            "batch_size=16777216",
            "compression_level=9",
            "llapi=true",
        ]:
            self.assertIn(expected_option, actual_options)
        with connection.schema_editor() as editor:
            editor.remove_index(IntegerArrayModel, index)
        self.assertNotIn(index_name, self.get_constraints(IntegerArrayModel._meta.db_table))
