
from django.contrib.auth import login, authenticate
from common.errors import ACCOUNT_REGISTRATION_ERRORS, UserRegistrationException

from common.shortcuts import response_json_success, response_json_error_with_message
from common.utilities import check_email_format

from domain.models import UserRegistration, UserAccount


def ajax_login_email_user(request, email, password):
    if not email:
        raise UserRegistrationException('email-notfound')

    if not password:
        raise UserRegistrationException('password-notfound')

    user = authenticate(email=email, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
        else:
            raise UserRegistrationException('user-inactive')
    else:
        raise UserRegistrationException('user-invalid')

    return user


def ajax_register_email_user(request, email):
    if not email:
        raise UserRegistrationException('email-notfound')

    if not check_email_format(email):
        raise UserRegistrationException('email-invalid')

    if UserRegistration.objects.filter(email=email).exists():
        raise UserRegistrationException('email-registering')

    if UserAccount.objects.filter(email=email).exists():
        raise UserRegistrationException('email-registered')

    registration = UserRegistration.objects.create_registration(email)
    registration.send_confirmation_email()

    return registration