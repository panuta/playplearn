# -*- encoding: utf-8 -*-

from django.shortcuts import render


def view_homepage(request):
    return render(request, 'page/homepage.html', {})