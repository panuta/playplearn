# -*- encoding: utf-8 -*-
from operator import itemgetter

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now

from common.utilities import split_filepath

from domain.models import Workshop, UserAccount
from presentation.forms import EditProfileForm, EditAccountEmailForm


@login_required
def view_my_profile(request):
    return _view_user_profile(request, request.user)


def view_user_profile(request, user_uid):
    user = get_object_or_404(UserAccount, uid=user_uid)
    return _view_user_profile(request, user)


def _view_user_profile(request, user):
    rightnow = now()

    teaching_workshops = Workshop.objects.filter(teacher=user, status='PUBLISHED').order_by('-first_published')

    attending_workshops = CourseEnrollment.objects.filter(student=user, is_public=True, status='CONFIRMED', schedule__start_datetime__gt=rightnow)
    attended_workshops = CourseEnrollment.objects.filter(student=user, is_public=True, status='CONFIRMED', schedule__start_datetime__lte=rightnow)

    return render(request, 'user/profile.html', {
        'context_user': user,
        'teaching_workshops': teaching_workshops,
        'attending_workshops': attending_workshops,
        'attended_workshops': attended_workshops,
    })


@login_required
def edit_my_settings_profile(request):
    user = request.user

    if request.method == 'POST':
        submit_type = request.POST.get('submit')

        if submit_type == 'remove-avatar':
            user.avatar.delete()
            user.save()
            messages.success(request, u'Success! Your profile picture is removed.')
            return redirect('edit_my_settings_profile')

        else:
            form = EditProfileForm(request.POST, request.FILES)
            if form.is_valid():
                user.name = form.cleaned_data['name']
                user.headline = form.cleaned_data['headline']
                user.website = form.cleaned_data['website']
                user.phone_number = form.cleaned_data['phone_number']
                user.save()

                avatar = form.cleaned_data['avatar']
                if avatar:
                    (root, name, ext) = split_filepath(avatar.name)
                    user.avatar.save('avatar.%s' % ext, avatar)

                messages.success(request, u'Success! Your profile is updated.')
                return redirect('edit_my_settings_profile')

    else:
        form = EditProfileForm(initial={
            'name': user.name,
            'headline': user.headline,
            'website': user.website,
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
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            request.user.set_password(form.cleaned_data['new_password1'])
            request.user.save()

            messages.success(request, u'Success! Your password is changed.')
            return redirect('edit_my_password')

    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'user/settings/settings_password.html', {'form': form})


@login_required
def view_my_news_feed(request):
    return render(request, 'user/news_feed.html', {})