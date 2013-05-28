# -*- encoding: utf-8 -*-

from django.shortcuts import render
from domain.models import Course


def view_homepage(request):
    recent_courses = Course.objects.filter(status='PUBLISHED').order_by('-first_published')
    return render(request, 'page/homepage.html', {'recent_courses': recent_courses})