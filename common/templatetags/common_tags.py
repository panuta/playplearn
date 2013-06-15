# -*- encoding: utf-8 -*-
import datetime

from django import template
from django.utils.timezone import now

from common.l10n import th
from common.l10n.th import PROVINCE_LIST

register = template.Library()

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
def schedule_datetime(schedule):
    try:
        return u'<span class="date">%s, %d %s %d</span> <span class="time">เวลา %02d:%02d น.</span>' % (
            th.TH_WEEKDAY_NAME[schedule.start_datetime.isoweekday()],
            schedule.start_datetime.day,
            th.TH_MONTH_ABBR_NAME[schedule.start_datetime.month],
            schedule.start_datetime.year + 543,
            schedule.start_datetime.hour,
            schedule.start_datetime.minute
        )
    except ValueError:
        return ''


@register.simple_tag
def province_options(selected_province=''):
    options = []
    for province_tuple in PROVINCE_LIST:
        selected = ' selected="selected"' if selected_province == province_tuple[0] else ''
        options.append('<option value="%s"%s>%s</option>' %(province_tuple[0], selected, province_tuple[1]))

    return ''.join(options)


@register.simple_tag
def time_options(selected_datetime=''):
    options = []
    for hour in range(0, 24):
        for minute in (0, 30):
            selected = ' selected="selected"' if type(selected_datetime) is datetime.datetime and \
                selected_datetime.hour == hour and \
                selected_datetime.minute == minute else ''
            options.append('<option value="%02d-%02d"%s>%02d:%02d</option>' %(hour, minute, selected, hour, minute))

    return ''.join(options)