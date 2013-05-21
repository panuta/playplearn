# -*- encoding: utf-8 -*-

from django.shortcuts import render


def view_student_home(request):
    return render(request, 'user/dashboard/student_home.html', {})


def view_teacher_home(request):
    return render(request, 'user/dashboard/teacher_home.html', {})