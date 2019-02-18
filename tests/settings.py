# -*- coding: utf-8
from __future__ import absolute_import, unicode_literals

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
    'tests.restaurants',
]

SITE_ID = 1

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

STATIC_URL = '/static/'

TEST_RUNNER = 'tests.runner.DropSchemaDiscoverRunner'
