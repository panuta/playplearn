# -*- encoding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from domain.models import UserAccount


@login_required
def view_my_profile(request):
    return _view_user_profile(request, request.user)


def view_user_profile(request, user_uid):
    user = get_object_or_404(UserAccount, uid=user_uid)
    return _view_user_profile(request, user)


def _view_user_profile(request, user):
    return render(request, 'user/profile.html', {'context_user': user})


@login_required
def edit_my_profile(request):
    return render(request, 'user/settings/settings_profile.html', {})


@login_required
def edit_my_account(request):
    return render(request, 'user/settings/settings_profile.html', {})


@login_required
def view_my_news_feed(request):
    return render(request, 'user/news_feed.html', {})