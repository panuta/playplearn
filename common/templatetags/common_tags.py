# -*- encoding: utf-8 -*-
import datetime
import re

from django import template
from django.template.defaultfilters import safe
from django.utils.timezone import now
from common.constants.course import COURSE_ENROLLMENT_STATUS_MAP, COURSE_ENROLLMENT_PAYMENT_STATUS_MAP
from common.constants.feedback import FEEDBACK_FEELING_CHOICES, FEEDBACK_FEELING_MAP

from common.l10n import th
from common.l10n.th import PROVINCE_LIST
from common.utilities import format_datetime_string

register = template.Library()


# DATE & TIME ##########################################################################################################

@register.filter
def daysuntil(from_datetime):
    return (from_datetime - now()).days


@register.filter
def timepast(from_datetime):
    if from_datetime:
        return from_datetime < now()
    else:
        return ''


@register.filter
def timestamp(datetime):
    try:
        return safe(u'%d %s %d เวลา %02d:%02d' % (
            datetime.day,
            th.TH_MONTH_ABBR_NAME[datetime.month],
            datetime.year + 543,
            datetime.hour,
            datetime.minute
        ))
    except ValueError:
        return ''


@register.filter
def schedule_datetime(schedule):
    try:
        return safe(u'<span class="date">%s, %d %s %d</span> <span class="time">เวลา %02d:%02d น.</span>' % (
            th.TH_WEEKDAY_NAME[schedule.start_datetime.isoweekday()],
            schedule.start_datetime.day,
            th.TH_MONTH_ABBR_NAME[schedule.start_datetime.month],
            schedule.start_datetime.year + 543,
            schedule.start_datetime.hour,
            schedule.start_datetime.minute
        ))
    except ValueError:
        return ''


@register.filter
def datetime_string(datetime):
    return format_datetime_string(datetime)


@register.simple_tag
def time_options(selected_datetime=''):
    options = []
    for hour in range(0, 24):
        for minute in (0, 30):
            selected = ' selected="selected"' if type(selected_datetime) is datetime.datetime and \
                                                 selected_datetime.hour == hour and \
                                                 selected_datetime.minute == minute else ''
            options.append('<option value="%02d:%02d"%s>%02d:%02d</option>' %(hour, minute, selected, hour, minute))

    return ''.join(options)


# DATA #################################################################################################################

@register.simple_tag
def province_options(selected_province=''):
    options = []
    for province_tuple in PROVINCE_LIST:
        selected = ' selected="selected"' if selected_province == province_tuple[0] else ''
        options.append('<option value="%s"%s>%s</option>' %(province_tuple[0], selected, province_tuple[1]))

    return ''.join(options)


# COURSE STATUS ########################################################################################################

@register.filter
def enrollment_status(enrollment):
    return COURSE_ENROLLMENT_STATUS_MAP[enrollment.status]['name']


@register.filter
def enrollment_payment_status(enrollment):
    return COURSE_ENROLLMENT_PAYMENT_STATUS_MAP[enrollment.payment_status]['name']


# COURSE FEEDBACK ######################################################################################################

@register.filter
def feelings(feedback):
    feelings = []
    for feeling in feedback.feelings.split(','):
        if feeling in FEEDBACK_FEELING_MAP:
            feelings.append('<span class="%s">%s</span> ' % (feeling, FEEDBACK_FEELING_MAP[feeling]['name']))

    return safe(''.join(feelings))


@register.simple_tag
def feedback_feeling_checkboxes(feelings=''):
    feeling_list = feelings.split(',')

    li = []
    for feeling_tuple in FEEDBACK_FEELING_CHOICES:
        checked = ' checked="checked"' if feeling_tuple[0] in feeling_list else ''
        li.append('<li><label><input type="checkbox" value="%s"%s/> %s</label></li>' %(feeling_tuple[0], checked, feeling_tuple[1]))

    return ''.join(li)