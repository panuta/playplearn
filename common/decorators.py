from functools import wraps

from django.conf import settings
from django.shortcuts import redirect
from django.utils.decorators import available_attrs


def redirect_if_authenticated(function=None):
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated():
                return redirect(settings.LOGIN_REDIRECT_URL)

            return view_func(request, *args, **kwargs)

        return _wrapped_view
    return decorator(function)
