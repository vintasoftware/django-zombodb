# Based on https://github.com/SectorLabs/django-postgres-extra/

import importlib
import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import ProgrammingError
from django.db.backends.postgresql.base import \
    DatabaseWrapper as Psycopg2DatabaseWrapper


logger = logging.getLogger(__name__)


def _get_backend_base():
    """Gets the base class for the custom database back-end.
    This should be the Django PostgreSQL back-end. However,
    some people are already using a custom back-end from
    another package. We are nice people and expose an option
    that allows them to configure the back-end we base upon.
    As long as the specified base eventually also has
    the PostgreSQL back-end as a base, then everything should
    work as intended.
    """
    base_class_name = getattr(
        settings,
        'ZOMBODB_DJANGO_BACKEND_BASE',
        'django.db.backends.postgresql'
    )

    base_class_module = importlib.import_module(base_class_name + '.base')
    base_class = getattr(base_class_module, 'DatabaseWrapper', None)

    if not base_class:
        raise ImproperlyConfigured((
            '\'%s\' is not a valid database back-end.'
            ' The module does not define a DatabaseWrapper class.'
            ' Check the value of ZOMBODB_DJANGO_BACKEND_BASE.'
        ) % base_class_name)

    if isinstance(base_class, Psycopg2DatabaseWrapper):
        raise ImproperlyConfigured((
            '\'%s\' is not a valid database back-end.'
            ' It does inherit from the PostgreSQL back-end.'
            ' Check the value of ZOMBODB_DJANGO_BACKEND_BASE.'
        ) % base_class_name)

    return base_class


def _get_schema_editor_base():
    """Gets the base class for the schema editor.
    We have to use the configured base back-end's
    schema editor for this."""

    return _get_backend_base().SchemaEditorClass


class SchemaEditor(_get_schema_editor_base()):
    pass


class DatabaseWrapper(_get_backend_base()):
    """Wraps the standard PostgreSQL database back-end.
    Overrides the schema editor with our custom
    schema editor and makes sure the `zombodb`
    extension is enabled."""

    SchemaEditorClass = SchemaEditor

    def prepare_database(self):
        """Ran to prepare the configured database.
        This is where we enable the `zombodb` extension
        if it wasn't enabled yet."""

        super().prepare_database()
        with self.cursor() as cursor:
            try:
                cursor.execute('CREATE EXTENSION IF NOT EXISTS zombodb')
            except ProgrammingError:  # permission denied
                logger.warning(
                    'Failed to create "zombodb" extension. '
                    'Have you installed it? If so,'
                    'make sure you are connected '
                    'to the database as a superuser '
                    'or add the extension manually.',
                    exc_info=True)
