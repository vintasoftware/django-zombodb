from django.apps import apps
from django.test import TestCase, modify_settings


@modify_settings(INSTALLED_APPS={'append': 'django_zombodb'})
class AppsTests(TestCase):

    def test_apps(self):
        app = apps.get_app_config('django_zombodb')
        self.assertEqual(app.name, 'django_zombodb')
