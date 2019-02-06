from django.test import TestCase, override_settings
from django.core.exceptions import ImproperlyConfigured

from django_zombodb.indexes import ZomboDBIndex

from .models import DateTimeArrayModel


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

    def test_not_eq(self):
        index_with_default_url = ZomboDBIndex(fields=['title'])
        index_with_other_url = ZomboDBIndex(fields=['title'], url='http://localhost/')
        self.assertNotEqual(index_with_default_url, index_with_other_url)

    def test_name_auto_generation(self):
        index = ZomboDBIndex(fields=['datetimes'])
        index.set_name_with_model(DateTimeArrayModel)
        self.assertEqual(index.name, 'tests_datet_datetim_889872_zombodb')

    def test_deconstruction(self):
        index = ZomboDBIndex(
            fields=['title'],
            name='test_title_zombodb',
            url='http://localhost/',
            shards=2,
            replicas=2,
            alias='test-alias',
            refresh_interval='10',
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
                'name': 'test_title_zombodb',
                'url': 'http://localhost/',
                'shards': 2,
                'replicas': 2,
                'alias': 'test-alias',
                'refresh_interval': '10',
                'type_name': 'test-doc',
                'bulk_concurrency': 20,
                'batch_size': 8388608 * 2,
                'compression_level': 9,
                'llapi': True,
            }
        )

    @override_settings(ZOMBODB_ELASTICSEARCH_URL='http://localhost:0')
    def test_deconstruct_no_args(self):
        index = ZomboDBIndex(fields=['title'], name='test_title_zombodb')
        path, args, kwargs = index.deconstruct()
        self.assertEqual(path, 'django_zombodb.indexes.ZomboDBIndex')
        self.assertEqual(args, ())
        self.assertEqual(
            kwargs,
            {
                'fields': ['title'],
                'name': 'test_title_zombodb',
                'url': 'http://localhost:0'
            }
        )


class ZomboDBIndexNoURLTests(TestCase):

    def test_exception_no_url(self):
        with self.assertRaises(ImproperlyConfigured) as cm:
            ZomboDBIndex(fields=['title'], name='test_title_zombodb')
        self.assertEqual(
            str(cm.exception),
            "Please set ZOMBODB_ELASTICSEARCH_URL on settings or "
            "pass a `url` argument for this index")
