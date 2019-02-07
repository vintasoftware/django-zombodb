import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection

from restaurants.models import Restaurant


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        csv_file_path = os.path.join(
            settings.BASE_DIR,
            'restaurants',
            'data',
            'yellowpages_com-restaurant_sample.csv')

        with connection.cursor() as cursor:
            cursor.execute('''
                CREATE TEMPORARY TABLE t (
                    id uuid,
                    url text,
                    name text,
                    street text,
                    zip_code text,
                    city text,
                    state text,
                    phone text,
                    email text,
                    website text,
                    categories text
                );
            ''')

            with open(csv_file_path) as csv_file:
                cursor.copy_expert(
                    "COPY t FROM stdin DELIMITER ',' CSV HEADER", csv_file)

            cursor.execute('''
                INSERT INTO restaurants_restaurant(
                    id,
                    url,
                    name,
                    street,
                    zip_code,
                    city,
                    state,
                    phone,
                    email,
                    website,
                    categories
                )
                SELECT
                    id,
                    url,
                    name,
                    street,
                    zip_code,
                    city,
                    state,
                    phone,
                    email,
                    COALESCE(website, ''),
                    regexp_split_to_array(categories, '\\s*,\\s*')
                FROM t;
            ''')

        count = Restaurant.objects.count()
        self.stdout.write(
            self.style.SUCCESS('Successfully created %s Restaurants' % count))
