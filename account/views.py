from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME, authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from common.decorators import redirect_if_authenticated
from common.errors import UserRegistrationException, ACCOUNT_REGISTRATION_ERRORS
from common.shortcuts import response_json_success, response_json_error_with_message
from common.utilities import split_filepath

from .forms import EmailAuthenticationForm, EmailSignupForm, EmailSignupResendForm, EmailUserActivationForm
from .functions import ajax_login_email_user, ajax_register_email_user
from .models import UserRegistration


@redirect_if_authenticated
def view_user_login(request, action):
    if request.method == 'POST':
        if action == 'signup':
            signup_form = EmailSignupForm(request.POST)
            if signup_form.is_valid():
                email = signup_form.cleaned_data['email']
                registration = UserRegistration.objects.create_registration(email)
                registration.send_confirmation_email()
                return redirect('view_user_signup_done')

        else:
            signup_form = EmailSignupForm()

        if action == 'resend':
            signup_form = EmailSignupResendForm(request.POST)
            if signup_form.is_valid():
                email = signup_form.cleaned_data['email']
                registration = UserRegistration.objects.get(email=email)
                registration.send_confirmation_email()
                return redirect('view_user_signup_done')

        if action == 'login':
            from django.contrib.auth.views import login
            response = login(request,
                             authentication_form=EmailAuthenticationForm,
                             template_name='account/registration/registration_login.html',
                             extra_context={'signup_form': signup_form})
            return response
        else:
            form = EmailAuthenticationForm()

        next = request.POST.get(REDIRECT_FIELD_NAME, '/')

    else:
        form = EmailAuthenticationForm()
        signup_form = EmailSignupForm()
        next = request.GET.get(REDIRECT_FIELD_NAME, '/')

    return render(request, 'account/registration/registration_login.html', {
        'form': form,
        'signup_form': signup_form,
        'next': next,
    })


def login_facebook(request):
    if request.GET.get('next'):
        request.session['facebook_next'] = request.GET.get('next')

    from social_auth.views import auth
    return auth(request, 'facebook')


def login_facebook_redirect(request):
    if request.session.get('facebook_next'):
        url = request.session.get('facebook_next')
    else:
        url = settings.LOGIN_REDIRECT_URL

    return redirect(url)


@redirect_if_authenticated
def view_user_signup_done(request):
    return render(request, 'account/registration/registration_signup_done.html', {})


@redirect_if_authenticated
def activate_email_user(request, key):
    user_registration = get_object_or_404(UserRegistration, registration_key=key)

    if request.method == 'POST':
        form = EmailUserActivationForm(request.POST, request.FILES)
        if form.is_valid():
            fullname = form.cleaned_data['fullname']
            password = form.cleaned_data['password']

            user_account = user_registration.claim_registration(fullname, password)

            avatar = form.cleaned_data['avatar']
            if avatar:
                (root, name, ext) = split_filepath(avatar.name)
                user_account.avatar.save('avatar.%s' % ext, avatar)

            user = authenticate(email=user_account.email, password=password)
            login(request, user)

            try:
                unauthenticated_enrollment = UnauthenticatedCourseEnrollment.objects.get(key=key)
            except UnauthenticatedCourseEnrollment.DoesNotExist:
                pass
            else:
                enrollment = CourseEnrollment.objects.create_enrollment_from_unauthenticated(request.user, unauthenticated_enrollment)
                unauthenticated_enrollment.delete()
                return redirect('view_course_outline_with_payment', enrollment.schedule.course.uid, enrollment.code)

            return redirect(settings.LOGIN_REDIRECT_URL)

    else:
        form = EmailUserActivationForm()

    return render(request, 'account/registration/registration_activate_email.html', {'form': form})


@require_POST
def ajax_email_login(request):
    if request.user.is_authenticated():
        return response_json_success()

    email = request.POST.get('email')
    password = request.POST.get('password')

    try:
        ajax_login_email_user(request, email, password)
    except UserRegistrationException, e:
        return response_json_error_with_message(e.exception_code, ACCOUNT_REGISTRATION_ERRORS)

    return response_json_success()


@require_POST
def ajax_email_register(request):
    if request.user.is_authenticated():
        return response_json_success()

    email = request.POST.get('email')

    try:
        ajax_register_email_user(request, email)
    except UserRegistrationException, e:
        return response_json_error_with_message(e.exception_code, ACCOUNT_REGISTRATION_ERRORS)

    return response_json_success()