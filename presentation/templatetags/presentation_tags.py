from django import template

from common.constants.course import COURSE_LEVEL_MAP
from common.constants.currency import CURRENCY_CODE_MAP

from domain.models import UserRegistration, CourseReservation

register = template.Library()


@register.assignment_tag
def to_resend_registration(registering_email):
    print 'TEST %s' % registering_email
    print UserRegistration.objects.filter(email=registering_email).count()
    return UserRegistration.objects.filter(email=registering_email).count()


# COURSE ###############################################################################################################

@register.simple_tag
def course_level(course):
    return COURSE_LEVEL_MAP[course.level]['name']


@register.simple_tag
def course_full_price(course):
    unit = CURRENCY_CODE_MAP[course.price_unit]
    return '%s%d %s' % (unit['symbol'], course.price, unit['name'])

# COURSE RESERVATION ###################################################################################################

@register.assignment_tag
def return_matching_reservation(user, schedule):
    reservations = CourseReservation.objects.filter(student=user, schedule=schedule)
    return reservations[0]

