from django.contrib import admin
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import RequestFactory
from django.utils.http import urlencode

from django_zombodb.admin_mixins import ZomboDBAdminMixin

from .restaurants.admin import RestaurantAdmin
from .restaurants.models import Restaurant


class AdminMixinsTests(TestCase):
    factory = RequestFactory()

    @classmethod
    def setUpTestData(cls):
        cls.superuser = User.objects.create_superuser(
            username='super', email='a@b.com', password='xxx')

        cls.alcove = Restaurant.objects.create(
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
        cls.tj = Restaurant.objects.create(
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
        cls.soleil = Restaurant.objects.create(
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

    def setUp(self):
        self.client.force_login(self.superuser)

    def _mocked_authenticated_request(self, url, user):
        request = self.factory.get(url)
        request.user = user
        return request

    def test_inherits_from_mixin(self):
        self.assertTrue(issubclass(RestaurantAdmin, ZomboDBAdminMixin))

    def test_no_search(self):
        restaurant_admin = RestaurantAdmin(Restaurant, admin.site)
        request = self._mocked_authenticated_request(
            '/restaurant/', self.superuser)
        cl = restaurant_admin.get_changelist_instance(request)
        queryset = cl.get_queryset(request)
        self.assertCountEqual(queryset, [self.alcove, self.tj, self.soleil])

    def test_get_search_results(self):
        restaurant_admin = RestaurantAdmin(Restaurant, admin.site)
        search_query = urlencode({
            'q': 'sushi asian japanese 11377'
        })
        request = self._mocked_authenticated_request(
            '/restaurant/?' + search_query, self.superuser)
        cl = restaurant_admin.get_changelist_instance(request)
        queryset = cl.get_queryset(request)
        self.assertEqual(list(queryset), [self.tj, self.soleil])

    def test_no_search_annotates_zombodb_score_as_0(self):
        restaurant_admin = RestaurantAdmin(Restaurant, admin.site)
        request = self._mocked_authenticated_request(
            '/restaurant/', self.superuser)
        cl = restaurant_admin.get_changelist_instance(request)
        queryset = cl.get_queryset(request)
        self.assertCountEqual(queryset, [self.alcove, self.tj, self.soleil])
        for restaurant in queryset:
            self.assertTrue(hasattr(restaurant, 'zombodb_score'))
            self.assertEqual(restaurant.zombodb_score, 0)

    def test_search_annotates_zombodb_score(self):
        restaurant_admin = RestaurantAdmin(Restaurant, admin.site)
        search_query = urlencode({
            'q': 'sushi asian japanese 11377'
        })
        request = self._mocked_authenticated_request(
            '/restaurant/?' + search_query, self.superuser)
        cl = restaurant_admin.get_changelist_instance(request)
        queryset = cl.get_queryset(request)
        self.assertEqual(list(queryset), [self.tj, self.soleil])
        for restaurant in queryset:
            self.assertTrue(hasattr(restaurant, 'zombodb_score'))
            self.assertGreater(restaurant.zombodb_score, 0)
