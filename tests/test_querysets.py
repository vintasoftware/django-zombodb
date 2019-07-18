from django.core.exceptions import ImproperlyConfigured
from django.test import TransactionTestCase, override_settings

from elasticsearch_dsl import Q as ElasticsearchQ
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Term

from django_zombodb.exceptions import InvalidElasticsearchQuery

from .restaurants.models import Restaurant, RestaurantNoIndex


@override_settings(ZOMBODB_ELASTICSEARCH_URL='http://localhost:9200/')
class SearchQuerySetTests(TransactionTestCase):

    def setUp(self):
        self.alcove = Restaurant.objects.create(
            url='http://example.org?thealcove',
            name='The Alcove',
            street='41-11 49th St',
            zip_code='11104',
            city='New York City',
            state='NY',
            phone='+1 347-813-4159',
            email='alcove@example.org',
            website='https://www.facebook.com/thealcoveny/',
            categories=['Gastropub', 'Tapas', 'Bar'],
        )
        self.tj = Restaurant.objects.create(
            url='http://example.org?tjasianbistro',
            name='TJ Asian Bistro',
            street='50-19 Skillman Ave',
            zip_code='11377',
            city='New York City',
            state='NY',
            phone='+1 718-205-2088',
            email='tjasianbistro@example.org',
            website='http://www.tjsushi.com/',
            categories=['Sushi', 'Asian', 'Japanese'],
        )
        self.soleil = Restaurant.objects.create(
            url='http://example.org?cotesoleil',
            name='Côté Soleil',
            street='50-12 Skillman Ave',
            zip_code='11377',
            city='New York City',
            state='NY',
            phone='+1 347-612-4333',
            email='cotesoleilnyc@example.org',
            website='https://cotesoleilnyc.com/',
            categories=['French', 'Coffee', 'European'],
        )

    def test_query_string_search(self):
        results = Restaurant.objects.query_string_search('coffee')
        self.assertCountEqual(results, [self.soleil])

        results = Restaurant.objects.query_string_search('11377')
        self.assertCountEqual(results, [self.tj, self.soleil])

        results = Restaurant.objects.query_string_search('email:alcove@example.org')
        self.assertCountEqual(results, [self.alcove])

    def test_dict_search(self):
        results = Restaurant.objects.dict_search(
            {'bool': {'must': [{'match': {'street': 'Skillman Ave'}},
                               {'match': {'categories': 'French'}}]}}
        )
        self.assertCountEqual(results, [self.soleil])

        results = Restaurant.objects.dict_search(
            {'bool': {'must': [{'match': {'street': 'Skillman Ave'}},
                               {'match': {'zip_code': '11377'}}]}}
        )
        self.assertCountEqual(results, [self.tj, self.soleil])

        results = Restaurant.objects.dict_search(
            {'term': {'email': 'alcove@example.org'}}
        )
        self.assertCountEqual(results, [self.alcove])

    def test_dsl_search(self):
        results = Restaurant.objects.dsl_search(ElasticsearchQ(
            'bool',
            must=[
                ElasticsearchQ('match', street='Skillman Ave'),
                ElasticsearchQ('match', categories='French')
            ]
        ))
        self.assertCountEqual(results, [self.soleil])

        results = Restaurant.objects.dsl_search(ElasticsearchQ(
            'bool',
            must=[
                ElasticsearchQ('match', street='Skillman Ave'),
                ElasticsearchQ('match', zip_code='11377')
            ]
        ))
        self.assertCountEqual(results, [self.tj, self.soleil])

        results = Restaurant.objects.dsl_search(Term(email='alcove@example.org'))
        self.assertCountEqual(results, [self.alcove])

    def test_query_string_search_sort(self):
        results = Restaurant.objects.query_string_search(
            'sushi OR asian OR japanese OR french',
            validate=True,
            sort=True)
        self.assertEqual(list(results), [self.tj, self.soleil])

        results = Restaurant.objects.query_string_search(
            'french OR coffee OR european OR sushi',
            validate=True,
            sort=True)
        self.assertEqual(list(results), [self.soleil, self.tj])

    def test_dict_search_sort(self):
        results = Restaurant.objects.dict_search(
            {'bool': {'minimum_should_match': 1,
             'should': [{'match': {'categories': 'sushi'}},
                        {'match': {'categories': 'asian'}},
                        {'match': {'categories': 'japanese'}},
                        {'match': {'categories': 'french'}}]}},
            validate=True,
            sort=True)
        self.assertEqual(list(results), [self.tj, self.soleil])

        results = Restaurant.objects.dict_search(
            {'bool': {'minimum_should_match': 1,
             'should': [{'match': {'categories': 'french'}},
                        {'match': {'categories': 'coffee'}},
                        {'match': {'categories': 'european'}},
                        {'match': {'categories': 'sushi'}}]}},
            validate=True,
            sort=True)
        self.assertEqual(list(results), [self.soleil, self.tj])

    def test_dsl_search_sort(self):
        results = Restaurant.objects.dsl_search(
            ElasticsearchQ(
                'bool',
                should=[
                    ElasticsearchQ('match', categories='sushi'),
                    ElasticsearchQ('match', categories='asian'),
                    ElasticsearchQ('match', categories='japanese'),
                    ElasticsearchQ('match', categories='french'),
                ],
                minimum_should_match=1
            ),
            validate=True,
            sort=True)
        self.assertEqual(list(results), [self.tj, self.soleil])

        results = Restaurant.objects.dsl_search(
            ElasticsearchQ(
                'bool',
                should=[
                    ElasticsearchQ('match', categories='french'),
                    ElasticsearchQ('match', categories='coffee'),
                    ElasticsearchQ('match', categories='european'),
                    ElasticsearchQ('match', categories='sushi'),
                ],
                minimum_should_match=1
            ),
            sort=True)
        self.assertEqual(list(results), [self.soleil, self.tj])

    def test_query_string_search_score_attr(self):
        results = Restaurant.objects.query_string_search(
            'skillman',
            sort=True,
            score_attr='custom_score')

        self.assertEqual(len(results), 2)
        for r in results:
            self.assertTrue(hasattr(r, 'custom_score'))
            self.assertGreater(r.custom_score, 0)

    def test_dict_search_score_attr(self):
        results = Restaurant.objects.dict_search(
            {'match': {'street': 'skillman'}},
            sort=True,
            score_attr='custom_score')

        self.assertEqual(len(results), 2)
        for r in results:
            self.assertTrue(hasattr(r, 'custom_score'))
            self.assertGreater(r.custom_score, 0)

    def test_dsl_search_score_attr(self):
        results = Restaurant.objects.dsl_search(
            ElasticsearchQ('match', street='skillman'),
            sort=True,
            score_attr='custom_score')

        self.assertEqual(len(results), 2)
        for r in results:
            self.assertTrue(hasattr(r, 'custom_score'))
            self.assertGreater(r.custom_score, 0)

    def test_query_string_search_validate(self):
        with self.assertRaises(InvalidElasticsearchQuery) as cm:
            Restaurant.objects.query_string_search('skillman AND', validate=True)
        self.assertRegex(
            str(cm.exception),
            "Invalid Elasticsearch query: (.+)")

    def test_dict_search_validate(self):
        with self.assertRaises(InvalidElasticsearchQuery) as cm:
            Restaurant.objects.dict_search({'wrong': 'query'}, validate=True)
        self.assertRegex(
            str(cm.exception),
            "Invalid Elasticsearch query: (.+)")

    def test_dsl_search_validate(self):
        query = ElasticsearchQ('bool')
        query.name = 'wrong'
        with self.assertRaises(InvalidElasticsearchQuery) as cm:
            Restaurant.objects.dsl_search(query, validate=True)
        self.assertRegex(
            str(cm.exception),
            "Invalid Elasticsearch query: (.+)")

    def test_dsl_search_cant_use_es_search(self):
        query = Search(index="my-index") \
            .filter("term", category="search") \
            .query("match", title="python")   \
            .exclude("match", description="beta")
        with self.assertRaises(InvalidElasticsearchQuery) as cm:
            Restaurant.objects.dsl_search(query, validate=True)
        self.assertEqual(
            str(cm.exception),
            "Do not use the `Search` class. "
            "`query` must be an instance of a class inheriting from `DslBase`.")

    def test_filter_search_chain(self):
        results = Restaurant.objects.filter(
            zip_code='11377'
        ).query_string_search('coffee')
        self.assertCountEqual(results, [self.soleil])

    def test_search_fails_if_no_zombodb_index_in_model_and_validate(self):
        with self.assertRaises(ImproperlyConfigured) as cm:
            RestaurantNoIndex.objects.query_string_search('skillman', validate=True)
        self.assertEqual(
            str(cm.exception),
            "Can't find a ZomboDBIndex at model {model}. "
            "Did you forget it? ".format(model=RestaurantNoIndex))

    def test_query_string_search_no_limit(self):
        # duplicate tj and soleil
        self.tj.pk = None
        self.tj.save()
        self.soleil.pk = None
        self.soleil.save()

        results = Restaurant.objects.query_string_search(
            'skillman',
            sort=True,
            limit=None)

        self.assertEqual(len(results), 4)
        self.assertEqual(
            [r.name for r in results],
            [self.soleil.name, self.soleil.name, self.tj.name, self.tj.name])

    def test_query_string_search_limit(self):
        # duplicate tj and soleil
        self.tj.pk = None
        self.tj.save()
        self.soleil.pk = None
        self.soleil.save()

        results = Restaurant.objects.query_string_search(
            'skillman',
            sort=True,
            limit=2)

        self.assertEqual(len(results), 2)
        self.assertEqual([r.name for r in results], [self.soleil.name] * 2)

    def test_dict_search_no_limit(self):
        # duplicate tj and soleil
        self.tj.pk = None
        self.tj.save()
        self.soleil.pk = None
        self.soleil.save()

        results = Restaurant.objects.dict_search(
            {'match': {'street': 'skillman'}},
            sort=True,
            limit=None)

        self.assertEqual(len(results), 4)
        self.assertEqual(
            [r.name for r in results],
            [self.soleil.name, self.soleil.name, self.tj.name, self.tj.name])

    def test_dict_search_limit(self):
        # duplicate tj and soleil
        self.tj.pk = None
        self.tj.save()
        self.soleil.pk = None
        self.soleil.save()

        results = Restaurant.objects.dict_search(
            {'match': {'street': 'skillman'}},
            sort=True,
            limit=2)

        self.assertEqual(len(results), 2)
        self.assertEqual([r.name for r in results], [self.soleil.name] * 2)

    def test_dsl_search_no_limit(self):
        # duplicate tj and soleil
        self.tj.pk = None
        self.tj.save()
        self.soleil.pk = None
        self.soleil.save()

        results = Restaurant.objects.dsl_search(
            ElasticsearchQ('match', street='skillman'),
            sort=True,
            limit=None)

        self.assertEqual(len(results), 4)
        self.assertEqual(
            [r.name for r in results],
            [self.soleil.name, self.soleil.name, self.tj.name, self.tj.name])

    def test_dsl_search_limit(self):
        # duplicate tj and soleil
        self.tj.pk = None
        self.tj.save()
        self.soleil.pk = None
        self.soleil.save()

        results = Restaurant.objects.dsl_search(
            ElasticsearchQ('match', street='skillman'),
            sort=True,
            limit=2)

        self.assertEqual(len(results), 2)
        self.assertEqual([r.name for r in results], [self.soleil.name] * 2)
