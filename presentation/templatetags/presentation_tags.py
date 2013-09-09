# -*- encoding: utf-8 -*-

from datetime import timedelta, datetime

from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.defaultfilters import safe

from easy_thumbnails.files import get_thumbnailer

from common.constants.feedback import FEEDBACK_FEELING_MAP
from common.utilities import format_date_url_string, format_time_url_string

from domain.models import WorkshopTopic, Place, WorkshopPicture, UserRegistration, Workshop
from reservation.models import Schedule

register = template.Library()


@register.assignment_tag
def to_resend_registration(registering_email):
    return UserRegistration.objects.filter(email=registering_email).count()


# WORKSHOP #############################################################################################################

# STATUS

@register.filter
def workshop_status(status):
    if status == Workshop.STATUS_DRAFT:
        status_name = 'ฉบับร่าง'
        status_css = 'draft'
        status_icon = 'icon-pencil'
    elif status == Workshop.STATUS_WAIT_FOR_APPROVAL:
        status_name = 'รอการรับรอง'
        status_css = 'wait_for_approval'
        status_icon = 'icon-time'
    elif status == Workshop.STATUS_READY_TO_PUBLISH:
        status_name = 'พร้อมเปิดตัว'
        status_css = 'ready_to_publish'
        status_icon = 'icon-time'
    elif status == Workshop.STATUS_PUBLISHED:
        status_name = 'เปิดตัว'
        status_css = 'published'
        status_icon = 'icon-ok'
    else:
        status_name = ''
        status_css = ''
        status_icon = ''

    return safe('<span class="%s"><i class="%s"></i> %s</span>' % (status_css, status_icon, status_name))


# TOPIC

@register.simple_tag
def workshop_topic_as_option(workshop):
    options = []
    for topic in WorkshopTopic.objects.all():
        selected = ' selected="selected"' if workshop and topic in workshop.topics.all() else ''
        options.append('<option value="%s"%s data-desc="%s">%s</option>' %(topic.slug, selected, topic.description, topic.name))

    return ''.join(options)


@register.simple_tag
def course_topics_as_li(selected_topic_slug):
    li = []
    for school in WorkshopTopic.objects.all():
        active = ' class="active"' if school.slug == selected_topic_slug else ''
        li.append('<li%s><a href="%s">%s</a></li>' % (active, reverse('view_courses_browse_by_topic', args=[school.slug]), school.name))

    return ''.join(li)


# PICTURE

@register.simple_tag
def workshop_cover_picture_url(workshop, thumbnail_size):
    cover = workshop.cover_picture()
    if cover:
        return get_thumbnailer(cover.image)[thumbnail_size].url
    else:
        return '%simages/%s' % (settings.STATIC_URL, settings.WORKSHOP_DEFAULT_COVER[thumbnail_size]['file'])


@register.simple_tag
def workshop_pictures_ordering_as_comma_separated(workshop):
    return ','.join([picture.uid for picture in WorkshopPicture.objects.filter(workshop=workshop, mark_deleted=False)])


# PLACE

@register.assignment_tag
def has_user_defined_place(user):
    return Place.objects.filter(is_userdefined=True, created_by=user).exists()


@register.assignment_tag
def get_user_defined_place(user, workshop):
    if workshop and workshop.place and workshop.place.is_userdefined:
        return workshop.place

    if not workshop and not Place.objects.filter(is_userdefined=True, created_by=user).exists():
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
def workshop_place_as_option(place_type, teacher, workshop=None):
    if place_type == 'system':
        places = Place.objects.filter(is_userdefined=False, is_visible=True)
    elif place_type == 'userdefined':
        places = Place.objects.filter(is_userdefined=True, created_by=teacher, is_visible=True)
    else:
        places = []

    options = []
    for place in places:
        selected = ' selected="selected"' if workshop and workshop.place == place else ''
        options.append('<option value="%s"%s>%s</option>' %(place.id, selected, place.name))

    return ''.join(options)


@register.assignment_tag
def get_course_undefined_place(course):
    if course and course.pk:
        place = course.get_editing_place()
        return place if place and place.is_userdefined else Place()
    else:
        return Place()


# WORKSHOP SCHEDULE ####################################################################################################

@register.simple_tag
def workshop_schedule_seats_as_option(schedule):
    seats = schedule.seats_left
    if schedule.seats_left > settings.DISPLAY_MAXIMUM_SEATS_RESERVABLE:
        seats = settings.DISPLAY_MAXIMUM_SEATS_RESERVABLE

    options = []
    for i in range(1, seats + 1):
        options.append('<option value="%d">%d คน</option>' % (i, i))

    return ''.join(options)


@register.simple_tag
def workshop_schedule_start_date_as_comma_separated(schedules):
    return ','.join(['"%02d/%02d/%d"' % (schedule.start_datetime.day, schedule.start_datetime.month, schedule.start_datetime.year) for schedule in schedules])


@register.simple_tag
def workshop_schedule_times_on_same_date_as_li(schedule):
    schedules = Schedule.objects.filter(
        workshop=schedule.workshop,
        start_datetime__year=schedule.start_datetime.year,
        start_datetime__month=schedule.start_datetime.month,
        start_datetime__day=schedule.start_datetime.day,
        status=Schedule.STATUS_OPEN
    ).order_by('start_datetime')

    li = []
    for same_date_schedule in schedules:
        selected = ' class="selected"' if same_date_schedule == schedule else ''
        li.append('<li%s><a href="%s">%s</a></li>' % (
            selected,
            reverse('manage_workshop_schedule_datetime',
                    args=[schedule.workshop.uid,
                          format_date_url_string(schedule.start_datetime),
                          format_time_url_string(schedule.start_datetime)
                    ]),
            datetime.strftime(schedule.start_datetime, '%H:%M')
        ))

    return ''.join(li)


@register.filter
def workshop_schedule_end_datetime(schedule):
    return schedule.start_datetime + timedelta(hours=schedule.course.duration)


@register.assignment_tag
def get_upcoming_schedule(workshop):
    return workshop.get_upcoming_schedule()


@register.assignment_tag
def get_available_upcoming_schedule(workshop):
    return workshop.get_available_upcoming_schedule()


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
        feeling_name = FEEDBACK_FEELING_MAP.get(feeling)['name']
        if feeling_name:
            li.append('<li>%s</li>' % feeling_name)

    return ''.join(li)


@register.simple_tag
def feedback_feelings_as_em(feedback):
    em = []
    for feeling in feedback.feelings.split(','):
        feeling_name = FEEDBACK_FEELING_MAP.get(feeling)
        if feeling_name:
            em.append('<em>%s</em>' % feeling_name)

    return ', '.join(em)