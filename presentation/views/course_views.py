# -*- encoding: utf-8 -*-
from django.http import Http404

from django.shortcuts import render, get_object_or_404
from domain.models import Course, CourseReservation


def view_course_outline(request, course_uid):
    course = get_object_or_404(Course, uid=course_uid)

    if not course.can_view(request.user):
        raise Http404

    return render(request, 'course/course_outline.html', {'course': course})


def view_course_enroll(request):
    return render(request, 'course/course_enroll.html', {})


def view_course_enroll_receipt(request):
    return render(request, 'course/course_enroll_receipt.html', {})


def view_courses_explore(request):
    return render(request, 'course/course_browse.html', {})


def view_course_teach(request):
    return render(request, 'course/course_teach.html', {})


def search_course_topics(request):
    print request
    pass