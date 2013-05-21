# -*- encoding: utf-8 -*-

from django.shortcuts import render


def view_user_profile(request):
    return render(request, 'user/profile.html', {})


def edit_user_profile(request):
    return render(request, 'user/settings/settings_profile.html', {})


def edit_user_account(request):
    return render(request, 'user/settings/settings_profile.html', {})