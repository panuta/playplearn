from django import template

from domain.models import UserRegistration

register = template.Library()


@register.assignment_tag
def to_resend_registration(registering_email):
    print 'TEST %s' % registering_email
    print UserRegistration.objects.filter(email=registering_email).count()
    return UserRegistration.objects.filter(email=registering_email).count()
