# -*- encoding: utf-8 -*-

from datetime import timedelta

from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.defaultfilters import safe
from django.utils.translation import ugettext as _
from common.constants.course import COURSE_STATUS_MAP

from common.constants.currency import CURRENCY_CODE_MAP
from common.constants.feedback import FEEDBACK_FEELING_MAP

from domain.models import UserRegistration, CourseEnrollment, CourseSchool, Place, CoursePicture

register = template.Library()


@register.assignment_tag
def to_resend_registration(registering_email):
    return UserRegistration.objects.filter(email=registering_email).count()


# COURSE ###############################################################################################################

@register.simple_tag
def course_full_price(course):
    unit = CURRENCY_CODE_MAP[course.price_unit]
    return '%s%d %s' % (unit['symbol'], course.price, unit['name'])


@register.simple_tag
def course_school_as_option(course):
    options = []
    for school in CourseSchool.objects.all():
        selected = ' selected="selected"' if course and school in course.schools.all() else ''
        options.append('<option value="%s"%s data-desc="%s">%s</option>' %(school.slug, selected, school.description, school.name))

    return ''.join(options)


@register.simple_tag
def course_topics_as_li(selected_topic_slug):
    li = []
    for school in CourseSchool.objects.all():
        active = ' class="active"' if school.slug == selected_topic_slug else ''
        li.append('<li%s><a href="%s">%s</a></li>' % (active, reverse('view_courses_browse_by_topic', args=[school.slug]), school.name))

    return ''.join(li)


@register.assignment_tag
def has_user_defined_place(user):
    return Place.objects.filter(is_userdefined=True, created_by=user).exists()


@register.assignment_tag
def get_user_defined_place(user, course):
    if course and course.place and course.place.is_userdefined:
        return course.place

    if not course and not Place.objects.filter(is_userdefined=True, created_by=user).exists():
        return Place()

    return None


@register.assignment_tag
def is_display_place_form(user, course):
    has_userdefined_places = Place.objects.filter(is_userdefined=True, created_by=user).exists()

    if not course or not has_userdefined_places:
        return True
    elif course and course.place and course.place.is_userdefined:
        return True

    return False


@register.simple_tag
def course_place_as_option(place_type, teacher, course=None):
    if place_type == 'system':
        places = Place.objects.filter(is_userdefined=False, is_visible=True)
    elif place_type == 'userdefined':
        places = Place.objects.filter(is_userdefined=True, created_by=teacher)
    else:
        places = []

    options = []
    for place in places:
        selected = ' selected="selected"' if course and course.place == place else ''
        place_name = place.name if place.name else '(No name)'
        options.append('<option value="%s"%s>%s</option>' %(place.id, selected, place_name))

    return ''.join(options)


@register.assignment_tag
def get_course_undefined_place(course):
    if course and course.pk:
        place = course.get_editing_place()
        return place if place and place.is_userdefined else Place()
    else:
        return Place()


@register.simple_tag
def course_picture_ordering_as_comma_separated(course):
    return ','.join([picture.uid for picture in CoursePicture.objects.filter(course=course, mark_deleted=False)])


@register.filter
def course_status_as_span(course):
    return course_status_as_span_with_sign(course, False)


@register.filter
def course_status_as_span_with_sign(course, with_sign=True):
    status = COURSE_STATUS_MAP[course.status]

    if with_sign:
        if course.status == 'DRAFT':
            sign = '<i class="icon-edit-sign"></i>'
        elif course.status in ('WAIT_FOR_APPROVAL', 'READY_TO_PUBLISH', 'PUBLISHED'):
            sign = '<i class="icon-check-sign"></i>'
        else:
            sign = ''
    else:
        sign = ''

    return safe('<span class="style-course-status %s">%s%s</span>' % (status['css_class'], sign, _(status['name'])))


# COURSE SCHEDULE ######################################################################################################

@register.simple_tag
def course_schedule_start_datetime_as_comma_separated(schedules):
    return ','.join(['"%d/%d/%d"' % (schedule.start_datetime.year, schedule.start_datetime.month, schedule.start_datetime.day) for schedule in schedules])


@register.filter
def course_schedule_end_datetime(schedule):
    return schedule.start_datetime + timedelta(hours=schedule.course.duration)


# COURSE ENROLLMENT ####################################################################################################

@register.simple_tag
def course_enrollment_people_as_option(schedule):
    seats_left = schedule.stats_seats_left()

    options = []
    for i in range(1, settings.ENROLLMENT_PEOPLE_LIMIT + 1):
        if i > seats_left:
            break

        options.append(u'<option value="%d">%d คน</option>' % (i, i))

    return ''.join(options)


@register.assignment_tag
def return_matching_enrollment(user, schedule):
    enrollments = CourseEnrollment.objects.filter(student=user, schedule=schedule)
    return enrollments[0]


# COURSE FEEDBACK ######################################################################################################

@register.simple_tag
def feedback_feelings_as_li(feedback):
    li = []
    for feeling in feedback.feelings.split(','):
        feeling_name = FEEDBACK_FEELING_MAP.get(feeling)
        if feeling_name:
            li.append('<li>%s</li>' % feeling_name)

    return ''.join(li)
