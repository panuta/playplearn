# -*- encoding: utf-8 -*-
from operator import itemgetter

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now

from common.utilities import split_filepath

from domain.models import UserAccount, Course, CourseEnrollment
from presentation.forms import EditProfileForm, EditAccountEmailForm


@login_required
def view_my_profile(request, show):
    return _view_user_profile(request, request.user, show)


def view_user_profile(request, user_uid, show):
    user = get_object_or_404(UserAccount, uid=user_uid)
    return _view_user_profile(request, user, show)


def _view_user_profile(request, user, show):

    """
    if not show:
        if user.is_teaching:
            show teaching
        else:
            show attending
    else:
        if show == 'teaching':
            if user.is_teaching:
                show teaching
            else:
                redirect to not show
        elif show == 'attending':
            if user.is_teaching:
                show attending
            else:
                redirect to not show
    """

    user_is_teaching = user.stats_courses_teaching()

    if not show:
        if user_is_teaching:
            show = 'teaching'
        else:
            show = 'attending'
    else:
        if show == 'attending' and not user_is_teaching:
            if user == request.user:
                return redirect('view_my_profile')
            else:
                return redirect('view_user_profile', user_uid=user.uid)

    context = {
        'context_user': user,
        'user_is_teaching': user_is_teaching,
        'show': show,
    }

    if show == 'teaching':
        teaching_courses = Course.objects.filter(teacher=user, status='PUBLISHED').order_by('-first_published')

        return render(request, 'user/profile_courses_teaching.html', dict(context.items() + {
            'teaching_courses': teaching_courses
        }.items()))

    elif show == 'attending':
        rightnow = now()

        sorting_attending_courses = {}
        sorting_attended_courses = {}
        for enrollment in CourseEnrollment.objects.filter(student=user, is_public=True, status='CONFIRMED'):
            course = enrollment.schedule.course

            if enrollment.schedule.start_datetime <= rightnow:
                sorting_courses = sorting_attended_courses
            else:
                sorting_courses = sorting_attending_courses

            if course.uid in sorting_courses:
                attend_tuple = sorting_courses[course.uid]
                attend_tuple[2].append(enrollment)

                if attend_tuple[1] < enrollment.schedule.start_datetime:
                    attend_tuple[1] = enrollment.schedule.start_datetime

            else:
                sorting_courses[course.uid] = (
                    enrollment.schedule.course,
                    enrollment.schedule.start_datetime,
                    [enrollment]
                )

        attending_courses = sorted(sorting_attending_courses.values(), key=itemgetter(1), reverse=True)
        attended_courses = sorted(sorting_attended_courses.values(), key=itemgetter(1), reverse=True)

        return render(request, 'user/profile_courses_attending.html', dict(context.items() + {
            'attending_courses': attending_courses,
            'attended_courses': attended_courses,
        }.items()))

    else:
        raise Http404


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