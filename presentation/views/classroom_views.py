# -*- encoding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def view_classroom_home(request):
    return render(request, 'classroom/classroom_home.html', {})


@login_required
def view_classroom_conversation(request):
    return render(request, 'classroom/classroom_conversation.html', {})


@login_required
def view_classroom_qa(request):
    return render(request, 'classroom/classroom_qa.html', {})


@login_required
def view_classroom_announcement(request):
    return render(request, 'classroom/classroom_announcement.html', {})
