# -*- encoding: utf-8 -*-

from django import forms
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _

from common.widgets import EmailWidget

from domain.models import UserRegistration, UserAccount


class EmailAuthenticationForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    email/password logins.
    """
    email = forms.EmailField(widget=EmailWidget(attrs={'name': 'email', 'placeholder': 'อีเมล'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'รหัสผ่าน'}))

    def __init__(self, request=None, *args, **kwargs):
        """
        If request is passed in, the form will validate that cookies are
        enabled. Note that the request (a HttpRequest object) must have set a
        cookie with the key TEST_COOKIE_NAME and value TEST_COOKIE_VALUE before
        running this validation.
        """
        self.request = request
        self.user_cache = None
        super(EmailAuthenticationForm, self).__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    _('Please enter a correct username and password. Note that both fields are case-sensitive.'))
            elif not self.user_cache.is_active:
                raise forms.ValidationError(_('This account is inactive.'))
        self.check_for_test_cookie()
        return self.cleaned_data

    def check_for_test_cookie(self):
        if self.request and not self.request.session.test_cookie_worked():
            raise forms.ValidationError(
                _('Your Web browser doesn\'t appear to have cookies enabled. Cookies are required for logging in.'))

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


class EmailSignupForm(forms.Form):
    email = forms.EmailField(widget=EmailWidget(attrs={'name': 'email', 'placeholder': 'อีเมล'}))

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if UserAccount.objects.filter(email=email).count():
            raise forms.ValidationError(_('This email is already registered.'))

        if UserRegistration.objects.filter(email=email).count():
            raise forms.ValidationError(_('This email is already signed up, but not yet activated.'))

        return email


class EmailSignupResendForm(forms.Form):
    email = forms.EmailField()

    def clean_signup_email(self):
        email = self.cleaned_data.get('email')

        if UserAccount.objects.filter(email=email).count():
            raise forms.ValidationError(_('This email is already registered.'))

        try:
            UserRegistration.objects.get(email=email)
        except UserRegistration.DoesNotExist:
            raise forms.ValidationError(_('This email is not yet requested to sign up.'))

        return email


class EmailUserActivationForm(forms.Form):
    avatar = forms.ImageField(required=False, widget=forms.FileInput)
    password = forms.CharField(max_length=100, widget=forms.PasswordInput)
    name = forms.CharField(max_length=100)