# -*- encoding: utf-8 -*-

from django import template
from django.utils.timezone import now

from common.l10n import th

register = template.Library()

@register.filter
def daysuntil(from_datetime):
    return (from_datetime - now()).days


@register.filter
def timepast(from_datetime):
    return from_datetime < now()


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