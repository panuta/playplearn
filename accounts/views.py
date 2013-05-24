from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME, authenticate, login
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404

from accounts.forms import EmailAuthenticationForm, EmailSignupForm, EmailSignupResendForm, EmailUserActivationForm
from common.decorators import redirect_if_authenticated
from common.utilities import split_filepath
from domain.models import UserRegistration


@redirect_if_authenticated
def view_login(request):
    if request.method == 'POST':
        from django.contrib.auth.views import login
        return login(request, authentication_form=EmailAuthenticationForm,
                     template_name='account/registration/registration_login.html')

    else:
        form = EmailAuthenticationForm()
        next = request.GET.get(REDIRECT_FIELD_NAME, '')

    return render(request, 'account/registration/registration_login.html',
                  {'form': form, 'next': next})


@redirect_if_authenticated
def view_signup(request):
    if request.method == 'POST':
        form = EmailSignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            registration = UserRegistration.objects.create_registration(email)
            registration.send_confirmation_email()

            return redirect('view_user_signup_done')

    else:
        form = EmailSignupForm()

    return render(request, 'account/registration/registration_signup.html',
                  {'form': form, 'next': next})


@redirect_if_authenticated
def view_signup_resend(request):
    if request.method == 'POST':
        form = EmailSignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            registration = UserRegistration.objects.get(email=email)
            registration.send_registration_request()

            return redirect('view_user_signup_done')

    else:
        raise Http404

    return render(request, 'account/registration/registration_signup.html',
                  {'form': form, 'next': next})


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
            name = form.cleaned_data['name']
            password = form.cleaned_data['password']

            user_account = user_registration.claim_registration(name, password)

            avatar = form.cleaned_data['avatar']
            if avatar:
                (root, name, ext) = split_filepath(avatar.name)
                user_account.avatar.save('avatar.%s' % ext, avatar)

            user = authenticate(email=user_account.email, password=password)
            login(request, user)

            return redirect(settings.LOGIN_REDIRECT_URL)

    else:
        form = EmailUserActivationForm()

    return render(request, 'account/registration/registration_activate_email.html', {'form':form})