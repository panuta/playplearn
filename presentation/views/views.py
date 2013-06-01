# -*- encoding: utf-8 -*-

from django.shortcuts import render, get_object_or_404
from domain.models import Course, Venue


def view_homepage(request):
    recent_courses = Course.objects.filter(status='PUBLISHED').order_by('-first_published')
    return render(request, 'page/homepage.html', {'recent_courses': recent_courses})


def view_venue_info_by_id(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id, is_visible=True)
    return _view_venue_info(request, venue)


def view_venue_info_by_code(request, venue_code):
    venue = get_object_or_404(Venue, code=venue_code, is_visible=True)
    return _view_venue_info(request, venue)


def _view_venue_info(request, venue):
    return render(request, 'page/venue_info.html', {'venue': venue})