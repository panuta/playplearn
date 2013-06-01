from functools import wraps

from django.conf import settings
from django.http import Http404
from django.shortcuts import redirect
from django.utils.decorators import available_attrs
from domain.models import Course


def redirect_if_authenticated(function=None):
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated():
                return redirect(settings.LOGIN_REDIRECT_URL)

            return view_func(request, *args, **kwargs)

        return _wrapped_view
    return decorator(function)


def teacher_or_student_only(function=None):
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            course_uid = kwargs.get('course_uid')

            try:
                course = Course.objects.get(uid=course_uid)
            except Course.DoesNotExist:
                raise Http404

            if course.teacher == request.user or course.schedules.filter(reservations__student=request.user).exists():
                return view_func(request, course, *args, **kwargs)

            raise Http404

        return _wrapped_view
    return decorator(function)


def teacher_only(function=None):
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            course_uid = kwargs.get('course_uid')

            try:
                course = Course.objects.get(uid=course_uid)
            except Course.DoesNotExist:
                raise Http404

            if course.teacher == request.user:
                return view_func(request, course, *args, **kwargs)

            raise Http404

        return _wrapped_view
    return decorator(function)