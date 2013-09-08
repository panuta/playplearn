# -*- encoding: utf-8 -*-
from operator import itemgetter
from django.conf import settings

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now
from easy_thumbnails.files import get_thumbnailer

from common.utilities import split_filepath

from domain.models import Workshop, UserAccount, WorkshopFeedback, user_avatar_dir
from presentation.forms import EditProfileForm, EditAccountEmailForm, EditAccountPasswordForm


@login_required
def view_my_profile(request):
    return _view_user_profile(request, request.user)


def view_user_profile(request, user_uid):
    user = get_object_or_404(UserAccount, uid=user_uid)
    return _view_user_profile(request, user)


def _view_user_profile(request, user):
    organizing_workshops = Workshop.objects.filter(
        teacher=user,
        status=Workshop.STATUS_PUBLISHED
    ).order_by('-date_published')

    feedbacks = WorkshopFeedback.objects.filter(reservation__user=user, is_visible=True).order_by('-created')

    return render(request, 'user/profile.html', {
        'context_user': user,
        'organizing_workshops': organizing_workshops,
        'feedbacks': feedbacks,
    })


@login_required
def edit_my_settings_profile(request):
    user = request.user

    if request.method == 'POST':
        submit_type = request.POST.get('submit')

        if submit_type == 'remove-avatar':
            user.avatar.delete()
            user.save()
            messages.success(request, u'ลบรูปผู้ใช้เรียบร้อย')
            return redirect('edit_my_settings_profile')

        else:
            form = EditProfileForm(request.POST, request.FILES)
            if form.is_valid():
                user.name = form.cleaned_data['name']
                user.about_me = form.cleaned_data['about_me']
                user.phone_number = form.cleaned_data['phone_number']
                user.save()

                avatar = form.cleaned_data['avatar']
                if avatar:
                    (root, name, ext) = split_filepath(avatar.name)
                    user.avatar.save('avatar.%s' % ext, avatar)

                messages.success(request, u'บันทึกการเปลี่ยนแปลงข้อมูลผู้ใช้เรียบร้อย')
                return redirect('edit_my_settings_profile')

    else:
        form = EditProfileForm(initial={
            'name': user.name,
            'about_me': user.about_me,
            'phone_number': user.phone_number,
        })

    return render(request, 'user/settings/settings_profile.html', {'form': form, })


@login_required
def edit_my_settings_social(request):
    return render(request, 'user/settings/settings_social.html', {})


@login_required
def edit_my_settings_notifications(request):
    return render(request, 'user/settings/settings_notifications.html', {})


@login_required
def edit_my_settings_account_email(request):
    if request.method == 'POST':
        form = EditAccountEmailForm(request.user, request.POST)
        if form.is_valid():
            # TODO Send email change confirmation email
            messages.success(request, u'Please check our confirmation email from your inbox')
    else:
        form = EditAccountEmailForm(request.user, initial={
            'email': request.user.email,
        })

    return render(request, 'user/settings/settings_account.html', {'form': form})


@login_required
def edit_my_settings_account_password(request):
    if request.method == 'POST':
        form = EditAccountPasswordForm(request.user, request.POST)
        if form.is_valid():
            request.user.set_password(form.cleaned_data['new_password1'])
            request.user.save()

            messages.success(request, u'เปลี่ยนรหัสผ่านเรียบร้อย')
            return redirect('edit_my_password')

    else:
        form = EditAccountPasswordForm(request.user)

    return render(request, 'user/settings/settings_password.html', {'form': form})


@login_required
def view_my_news_feed(request):
    return render(request, 'user/news_feed.html', {})