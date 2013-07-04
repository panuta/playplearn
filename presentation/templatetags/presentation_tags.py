from django import template
from django.core.urlresolvers import reverse

from common.constants.course import COURSE_LEVEL_MAP, COURSE_LEVEL_CHOICES
from common.constants.currency import CURRENCY_CODE_MAP
from common.constants.feedback import FEEDBACK_FEELING_MAP

from domain.models import UserRegistration, CourseEnrollment, CourseSchool, Place, EditingPlace

register = template.Library()


@register.assignment_tag
def to_resend_registration(registering_email):
    return UserRegistration.objects.filter(email=registering_email).count()


# COURSE ###############################################################################################################

@register.simple_tag
def course_topics_as_comma_separated(course):
    return ','.join([tag.name for tag in course.tags.all()]) if course else ''


@register.simple_tag
def course_level(course):
    return COURSE_LEVEL_MAP[course.level]['name']


@register.simple_tag
def course_level_options(course):
    options = []
    for level_tuple in COURSE_LEVEL_CHOICES:
        selected = ' selected="selected"' if course and course.level == level_tuple[0] else ''
        options.append('<option value="%s"%s>%s</option>' %(level_tuple[0], selected, level_tuple[1]))

    return ''.join(options)


@register.simple_tag
def course_full_price(course):
    unit = CURRENCY_CODE_MAP[course.price_unit]
    return '%s%d %s' % (unit['symbol'], course.price, unit['name'])


@register.simple_tag
def course_school_as_option(course):
    options = []
    for school in CourseSchool.objects.all():
        selected = ' selected="selected"' if course and school in course.schools.all() else ''
        options.append('<option value="%s"%s>%s</option>' %(school.slug, selected, school.name))

    return ''.join(options)


@register.simple_tag
def course_school_as_li(selected_school_slug):
    li = []
    for school in CourseSchool.objects.all():
        active = ' class="active"' if school.slug == selected_school_slug else ''
        li.append('<li%s><a href="%s">%s</a></li>' % (active, reverse('view_courses_browse_by_school', args=[school.slug]), school.name))

    return ''.join(li)


@register.simple_tag
def course_place_as_option(course):
    if course and course.pk:
        editing_place = course.get_editing_place()

        if isinstance(editing_place, EditingPlace):
            editing_place = editing_place.defined_place

    else:
        editing_place = None

    options = []
    for place in Place.objects.filter(is_userdefined=False, is_visible=True):
        selected = ' selected="selected"' if editing_place == place else ''
        options.append('<option value="%s"%s>%s</option>' %(place.id, selected, place.name))

    return ''.join(options)


@register.assignment_tag
def get_course_undefined_place(course):
    if course and course.pk:
        place = course.get_editing_place()
        return place if place and place.is_userdefined else Place()
    else:
        return Place()


# COURSE ENROLLMENT ####################################################################################################

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
