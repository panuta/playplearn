import json

from django.http import HttpResponse


def response_json(obj=None):
    if obj:
        return HttpResponse(json.dumps(obj))
    else:
        return HttpResponse('{}')


def response_json_success(return_object={}):
    return_object['status'] = 'success'
    return HttpResponse(json.dumps(return_object))


def response_json_error(error_code='', return_object={}):
    return_object['status'] = 'error'
    return_object['error'] = error_code
    return HttpResponse(json.dumps(return_object))