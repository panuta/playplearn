from django.conf import settings
from account.forms import EmailAuthenticationForm, EmailSignupForm


def site_settings(request):
    return {'settings': settings}


def registration_form(request):
    login_form = EmailAuthenticationForm()
    signup_form = EmailSignupForm()
    return {'login_form': login_form, 'signup_form': signup_form}