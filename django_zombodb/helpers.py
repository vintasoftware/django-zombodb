import json

from django.core.exceptions import ImproperlyConfigured
from django.db import connection
from django.utils.http import urlencode

from django_zombodb.indexes import ZomboDBIndex


def get_zombodb_index_from_model(model):
    for index in model._meta.indexes:
        if isinstance(index, ZomboDBIndex):
            break
    else:
        raise ImproperlyConfigured(
            "Can't find a ZomboDBIndex at model {model}. "
            "Did you forget it? ".format(model=model))

    return index


def validate_query_string(model, query):
    index = get_zombodb_index_from_model(model)

    with connection.cursor() as cursor:
        q = urlencode({'q': query})
        cursor.execute('''
            SELECT zdb.request(%(index_name)s, %(endpoint)s);
        ''', {
            'index_name': index.name,
            'endpoint': '_validate/query?' + q
        })
        validation_result = json.loads(cursor.fetchone()[0])
        return validation_result['valid']
