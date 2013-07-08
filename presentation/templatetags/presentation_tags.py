from django import template
from django.core.urlresolvers import reverse

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
        options.append('<option value="%s"%s>%s</option>' %(school.slug, selected, school.name))

    return ''.join(options)


@register.simple_tag
def course_school_as_li(selected_school_slug):
    li = []
    for school in CourseSchool.objects.all():
        active = ' class="active"' if school.slug == selected_school_slug else ''
        li.append('<li%s><a href="%s">%s</a></li>' % (active, reverse('view_courses_browse_by_school', args=[school.slug]), school.name))

    return ''.join(li)


@register.assignment_tag
def is_user_defined_place(user):
    return Place.objects.filter(is_userdefined=True, created_by=user).exists()


@register.assignment_tag
def is_display_place_form(user, course):
    has_userdefined_places = Place.objects.filter(is_userdefined=True, created_by=user).exists()

    if not course and not has_userdefined_places:
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


# COURSE SCHEDULE ######################################################################################################

@register.simple_tag
def course_schedule_start_datetime_as_comma_separated(schedules):
    return ','.join(['"%d/%d/%d"' % (schedule.start_datetime.year, schedule.start_datetime.month, schedule.start_datetime.day) for schedule in schedules])


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
