# -*- coding: utf-8
from __future__ import unicode_literals, absolute_import

import django

from decouple import config

DEBUG = False
USE_TZ = True

SECRET_KEY = 'test'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'USER': 'django_zombodb',
        'NAME': 'django_zombodb',
        'PASSWORD': 'password',
        'HOST': '127.0.0.1',
        'PORT': config('POSTGRES_PORT', default='5432'),
        'ATOMIC_REQUESTS': False,  # False gives better stacktraces
    }
}

ROOT_URLCONF = "tests.urls"

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_zombodb',

    'tests',
]

SITE_ID = 1

if django.VERSION >= (1, 10):
    MIDDLEWARE = ()
else:
    MIDDLEWARE_CLASSES = ()
