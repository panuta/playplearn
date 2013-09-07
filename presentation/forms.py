# -*- encoding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

from domain.models import UserAccount


# USER #################################################################################################################

class EditProfileForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    avatar = forms.ImageField(required=False, widget=forms.FileInput())
    about_me = forms.CharField(required=False, max_length=300, widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(required=False, max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))


class EditAccountEmailForm(forms.Form):
    email = forms.EmailField(max_length=100)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(EditAccountEmailForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()

        if UserAccount.objects.filter(email=email).exclude(id=self.user.id).exists():
            raise forms.ValidationError(_('This email has already been registered.'))

        return email


# WORKSHOP

class CreateFirstWorkshop(forms.Form):
    title = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'class': 'form-control'}))