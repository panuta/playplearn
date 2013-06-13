# -*- encoding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

from domain.models import UserAccount, Place


# USER #################################################################################################################

class EditProfileForm(forms.Form):
    avatar = forms.ImageField(required=False, widget=forms.FileInput())
    name = forms.CharField(max_length=100)
    headline = forms.CharField(max_length=300)
    website = forms.URLField(required=False, max_length=255)
    phone_number = forms.CharField(max_length=50)


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

