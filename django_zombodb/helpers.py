import json

from django.core.exceptions import ImproperlyConfigured
from django.db import connection

from elasticsearch.serializer import JSONSerializer

from django_zombodb.indexes import ZomboDBIndex


def get_zombodb_index_from_model(model):
    for index in model._meta.indexes:
        if isinstance(index, ZomboDBIndex):
            return index

    raise ImproperlyConfigured(
        "Can't find a ZomboDBIndex at model {model}. "
        "Did you forget it? ".format(model=model))


def validate_query(model, query_dict_or_query):
    json_serializer = JSONSerializer()
    if isinstance(query_dict_or_query, str):
        post_data = json_serializer.dumps(
            {'query': {'query_string': {'query': query_dict_or_query}}})
    else:
        post_data = json_serializer.dumps({'query': query_dict_or_query})

    index = get_zombodb_index_from_model(model)

    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT zdb.request(%(index_name)s, %(endpoint)s, 'POST', %(post_data)s);
        ''', {
            'index_name': index.name,
            'endpoint': '_validate/query',
            'post_data': post_data
        })
        validation_result = json.loads(cursor.fetchone()[0])
        return validation_result['valid']
