import json

from django.http import HttpResponse


def response_json(obj=None):
    if obj:
        return HttpResponse(json.dumps(obj))
    else:
        return HttpResponse('{}')


def response_json_success(return_object={}):
    return HttpResponse(json.dumps({
        'status': 'success',
        'data': return_object,
    }))


def response_json_error(error_code='', return_object={}):
    return HttpResponse(json.dumps({
        'status': 'error',
        'error': error_code,
        'data': return_object,
    }))