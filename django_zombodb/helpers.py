import json

from django.core.exceptions import ImproperlyConfigured
from django.db import connection

from elasticsearch.serializer import JSONSerializer

from django_zombodb.indexes import ZomboDBIndex


json_serializer = JSONSerializer()


def get_zombodb_index_from_model(model):
    for index in model._meta.indexes:
        if isinstance(index, ZomboDBIndex):
            return index

    raise ImproperlyConfigured(
        "Can't find a ZomboDBIndex at model {model}. "
        "Did you forget it? ".format(model=model))


def _validate_query(index, post_data):
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT zdb.request(%(index_name)s, %(endpoint)s, 'POST', %(post_data)s);
        ''', {
            'index_name': index.name,
            'endpoint': '_validate/query',
            'post_data': post_data
        })
        validation_result = json.loads(cursor.fetchone()[0])
        if 'error' in validation_result:
            raise ImproperlyConfigured(
                "Unexpected Elasticsearch error. "
                "You may need to recreate your index={index}. "
                "Details:\n"
                "{error}".format(index=index, error=validation_result))
        return validation_result['valid']


def validate_query_string(model, query):
    post_data = json_serializer.dumps(
        {'query': {'query_string': {'query': query}}})
    index = get_zombodb_index_from_model(model)

    return _validate_query(index, post_data)


def validate_query_dict(model, query):
    post_data = json_serializer.dumps({'query': query})
    index = get_zombodb_index_from_model(model)

    return _validate_query(index, post_data)
