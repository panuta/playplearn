# -*- encoding: utf-8 -*-

from django.shortcuts import render, get_object_or_404
from domain.models import Course, Place


def view_homepage(request):
    recent_courses = Course.objects.filter(status='PUBLISHED').order_by('-first_published')
    return render(request, 'page/homepage.html', {'recent_courses': recent_courses})


def view_place_info_by_id(request, place_id):
    place = get_object_or_404(Place, id=place_id, is_visible=True)
    return _view_place_info(request, place)


def view_place_info_by_code(request, place_code):
    place = get_object_or_404(Place, code=place_code, is_visible=True)
    return _view_place_info(request, place)


def _view_place_info(request, place):
    return render(request, 'page/place_info.html', {'place': place})