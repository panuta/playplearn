
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, authenticate
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from django.utils.http import is_safe_url
from django.views.decorators.http import require_POST

from common.decorators import redirect_if_authenticated
from common.errors import UserRegistrationException, ACCOUNT_REGISTRATION_ERRORS
from common.shortcuts import response_json_success, response_json_error_with_message
from common.utilities import split_filepath

from domain.models import UserRegistration

from .forms import EmailAuthenticationForm, EmailSignupForm, EmailSignupResendForm, EmailUserActivationForm
from .functions import ajax_login_email_user, ajax_register_email_user


@redirect_if_authenticated
def view_user_login(request, action):
    redirect_to = request.REQUEST.get(REDIRECT_FIELD_NAME, '/')

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
            login_form = EmailAuthenticationForm(data=request.POST)
            if login_form.is_valid():
                # Ensure the user-originating redirection url is safe.
                if not is_safe_url(url=redirect_to, host=request.get_host()):
                    redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

                auth_login(request, login_form.get_user())

                if request.session.test_cookie_worked():
                    request.session.delete_test_cookie()

                return HttpResponseRedirect(redirect_to)

        else:
            login_form = EmailAuthenticationForm()

    else:
        login_form = EmailAuthenticationForm()
        signup_form = EmailSignupForm()

    return render(request, 'account/registration/registration_login.html', {
        'login_form': login_form,
        'signup_form': signup_form,
        'redirect_to': redirect_to,
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
            auth_login(request, user)

            """
            try:
                unauthenticated_enrollment = UnauthenticatedCourseEnrollment.objects.get(key=key)
            except UnauthenticatedCourseEnrollment.DoesNotExist:
                pass
            else:
                enrollment = CourseEnrollment.objects.create_enrollment_from_unauthenticated(request.user, unauthenticated_enrollment)
                unauthenticated_enrollment.delete()
                return redirect('view_course_outline_with_payment', enrollment.schedule.course.uid, enrollment.code)
            """

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