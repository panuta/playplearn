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


def response_json_error_with_message(error_code, error_dict, return_object={}):
    message = error_dict[error_code]
    return HttpResponse(json.dumps({
        'status': 'error',
        'error': error_code,
        'message': message,
        'data': return_object,
    }))