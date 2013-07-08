# -*- encoding: utf-8 -*-

from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.utils.timezone import now

from domain.models import Place, CourseSchedule


def view_homepage(request):
    rightnow = now()

    upcoming_schedules = CourseSchedule.objects.filter(
        course__status='PUBLISHED',
        status='OPENING',
        start_datetime__gt=rightnow
    ).order_by('start_datetime')

    upcoming_courses = []
    for schedule in upcoming_schedules:
        if schedule.course not in upcoming_courses:
            upcoming_courses.append(schedule.course)

        if len(upcoming_courses) > settings.DISPLAY_HOMEPAGE_COURSES:
            break

    return render(request, 'page/homepage.html', {'upcoming_courses': upcoming_courses})


def view_place_info_by_id(request, place_id):
    place = get_object_or_404(Place, id=place_id, is_visible=True)
    return _view_place_info(request, place)


def view_place_info_by_code(request, place_code):
    place = get_object_or_404(Place, code=place_code, is_visible=True)
    return _view_place_info(request, place)


def _view_place_info(request, place):
    return render(request, 'page/place_info.html', {'place': place})