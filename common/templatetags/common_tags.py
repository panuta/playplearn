# -*- encoding: utf-8 -*-
import datetime

from django import template
from django.conf import settings
from django.template.defaultfilters import safe
from django.utils.timezone import now
from common.constants.workshop import WORKSHOP_ENROLLMENT_STATUS_MAP, WORKSHOP_ENROLLMENT_PAYMENT_STATUS_MAP
from common.constants.feedback import FEEDBACK_FEELING_CHOICES, FEEDBACK_FEELING_MAP
from common.constants.payment import BANK_ACCOUNT_LIST, BANK_ACCOUNT_MAP

from common.l10n import th
from common.l10n.th import PROVINCE_LIST, PROVINCE_MAP
from common.utilities import format_datetime_url_string, format_date_url_string, format_time_url_string, format_date_string, format_abbr_date, get_excerpt

register = template.Library()


# HTML ##########################################################################################################

@register.simple_tag
def thumbnail_img_size(thumbnail_name):
    (width, height) = settings.THUMBNAIL_ALIASES[''][thumbnail_name]['size']
    return 'width="%d" height="%d"' % (width, height)


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
def schedule_datetime_duration(schedule):
    try:
        start_datetime = schedule.start_datetime
        end_datetime = schedule.start_datetime + datetime.timedelta(hours=schedule.workshop.duration)

        return safe(u'<span class="date">%s, %d %s %d</span> <span class="time">เวลา %02d:%02d - %02d:%02d น. (%d ชั่วโมง)</span>' % (
            th.TH_WEEKDAY_NAME[start_datetime.isoweekday()],
            start_datetime.day,
            th.TH_MONTH_ABBR_NAME[start_datetime.month],
            start_datetime.year + 543,
            start_datetime.hour,
            start_datetime.minute,
            end_datetime.hour,
            end_datetime.minute,
            schedule.workshop.duration,
        ))
    except ValueError:
        return ''


@register.filter
def schedule_datetime_no_weekday(schedule):
    try:
        return safe(u'<span class="date">%d %s %d</span> <span class="time">เวลา %02d:%02d น.</span>' % (
            schedule.start_datetime.day,
            th.TH_MONTH_ABBR_NAME[schedule.start_datetime.month],
            schedule.start_datetime.year + 543,
            schedule.start_datetime.hour,
            schedule.start_datetime.minute
        ))
    except ValueError:
        return ''


@register.filter
def date_url_string(datetime):
    return format_date_url_string(datetime)


@register.filter
def time_url_string(datetime):
    return format_time_url_string(datetime)


@register.filter
def datetime_url_string(datetime):
    return format_datetime_url_string(datetime)


@register.simple_tag
def hour_as_options(selected_hour=''):
    options = []
    for hour in range(0, 24):
        selected = ' selected="selected"' if selected_hour == hour else ''
        options.append('<option value="%02d"%s>%02d</option>' %(hour, selected, hour))

    return ''.join(options)


@register.simple_tag
def minute_as_options(selected_minute=''):
    options = []
    for minute in (0, 15, 30, 45):
        selected = ' selected="selected"' if selected_minute == minute else ''
        options.append('<option value="%02d"%s>%02d</option>' %(minute, selected, minute))

    return ''.join(options)


@register.simple_tag
def time_options(selected_datetime=''):
    options = []
    for hour in range(0, 24):
        for minute in (0, 30):  # TODO Check if 30 number is correct?
            selected = ' selected="selected"' if type(selected_datetime) is datetime.datetime and \
                                                 selected_datetime.hour == hour and \
                                                 selected_datetime.minute == minute else ''
            options.append('<option value="%02d:%02d"%s>%02d:%02d</option>' %(hour, minute, selected, hour, minute))

    return ''.join(options)


@register.simple_tag
def date_from_today_as_option():
    rightnow = now()
    options = [
        u'<option value="%s">วันนี้ - %s</option>' % (
            format_date_string(rightnow),
            format_abbr_date(rightnow)
        ),
        u'<option value="%s">เมื่อวาน - %s</option>' % (
            format_date_string(rightnow + datetime.timedelta(days=-1)),
            format_abbr_date(rightnow + datetime.timedelta(days=-1))
        ),
    ]

    for i in range(-2, -3, -1):
        options.append(u'<option value="%s">%s</option>' % (
            format_date_string(rightnow + datetime.timedelta(days=i)),
            format_abbr_date(rightnow + datetime.timedelta(days=i))
        ))

    return ''.join(options)

@register.simple_tag
def time_hour_as_option():
    options = []
    for hour in range(0, 24):
        options.append('<option value="%02d">%02d</option>' % (hour, hour))
    return ''.join(options)


@register.simple_tag
def time_minute_as_option():
    options = []
    for minute in range(0, 60):
        options.append('<option value="%02d">%02d</option>' % (minute, minute))
    return ''.join(options)


# NUMBER ###############################################################################################################

@register.filter
def format_price(number):
    if not (number - int(number)):
        return '{:,}'.format(int(number))
    else:
        return '{:,.2f}'.format(number)


# TEXT #################################################################################################################

@register.filter
def excerpt(content, limit):
    excerpt, was_cut = get_excerpt(content, limit)

    if was_cut:
        return u'%s ...' % excerpt
    else:
        return excerpt

# DATA #################################################################################################################

@register.simple_tag
def province_options(selected_province=''):
    options = []
    for province_tuple in PROVINCE_LIST:
        selected = ' selected="selected"' if selected_province == province_tuple[0] else ''
        options.append('<option value="%s"%s>%s</option>' %(province_tuple[0], selected, province_tuple[1]))

    return ''.join(options)


@register.filter
def province_name(province_code):
    return PROVINCE_MAP.get(province_code)


@register.assignment_tag
def bank_account_assign():
    return BANK_ACCOUNT_MAP.values()


@register.simple_tag
def bank_account_as_option():
    options = []
    for bank_account_tuple in BANK_ACCOUNT_LIST:
        options.append('<option value="%s">%s</option>' %(bank_account_tuple[0], bank_account_tuple[1]))
    return ''.join(options)


# USER #######

@register.filter()
def name_or_me(user, logged_in_user):
    if logged_in_user.id == user.id:
        return 'Me'
    else:
        return user.name


# COURSE STATUS ########################################################################################################

@register.filter
def enrollment_status_for_student(enrollment):
    if enrollment.payment_status == 'WAIT_FOR_PAYMENT':
        return WORKSHOP_ENROLLMENT_PAYMENT_STATUS_MAP['WAIT_FOR_PAYMENT']['name']

    return WORKSHOP_ENROLLMENT_STATUS_MAP[enrollment.status]['name']


@register.filter
def enrollment_status(enrollment):
    return WORKSHOP_ENROLLMENT_STATUS_MAP[enrollment.status]['name']


@register.filter
def enrollment_payment_status(enrollment):
    return WORKSHOP_ENROLLMENT_PAYMENT_STATUS_MAP[enrollment.payment_status]['name']


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