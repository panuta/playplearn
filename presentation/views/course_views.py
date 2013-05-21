# -*- encoding: utf-8 -*-

from django.shortcuts import render


def view_course_outline(request):
    return render(request, 'course/course_outline.html', {})


def view_course_enroll(request):
    return render(request, 'course/course_enroll.html', {})


def view_course_explorer(request):
    return render(request, 'course/course_explorer.html', {})


def view_course_teach(request):
    return render(request, 'course/course_teach.html', {})