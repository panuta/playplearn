# -*- encoding: utf-8 -*-

import os

from common.constants import datetime as datetime_constants

from common.l10n import th


SHORTUUID_ALPHABETS_NUMBER_ONLY = '1234567890'
SHORTUUID_ALPHABETS_CHARACTERS_NUMBER = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'


# DATE & TIME ##########################################################################################################

def format_full_datetime(datetime):
    try:
        return u'%s, %d %s %d เวลา %02d:%02d น.' % (
            th.TH_WEEKDAY_NAME[datetime.isoweekday()],
            datetime.day,
            th.TH_MONTH_ABBR_NAME[datetime.month],
            datetime.year + 543,
            datetime.hour,
            datetime.minute
        )
    except ValueError:
        return ''


def format_abbr_date(datetime):
    try:
        return u'%d %s %d' % (
            datetime.day,
            th.TH_MONTH_ABBR_NAME[datetime.month],
            datetime.year + 543,
        )
    except ValueError:
        return ''


def format_datetime_string(datetime):
    try:
        return '%d_%02d_%02d_%02d_%02d' % (
            datetime.year,
            datetime.month,
            datetime.day,
            datetime.hour,
            datetime.minute,
        )
    except ValueError:
        return ''


def format_date_string(datetime):
    try:
        return '%d-%02d-%02d' % (
            datetime.year,
            datetime.month,
            datetime.day,
        )
    except ValueError:
        return ''


"""
def format_full_datetime(datetime):
    try:
        return u'%d %s %d เวลา %02d:%02d น.' % (datetime.day, datetime_constants.THAI_MONTH_NAME[datetime.month], datetime.year + 543, datetime.hour, datetime.minute)
    except:
        return ''


def format_abbr_datetime(datetime):
    try:
        return u'%d %s %d เวลา %02d:%02d น.' % (datetime.day, datetime_constants.THAI_MONTH_ABBR_NAME[datetime.month], datetime.year + 543, datetime.hour, datetime.minute)
    except:
        return ''


def format_full_date(datetime):
    try:
        return u'%d %s %d' % (datetime.day, datetime_constants.THAI_MONTH_NAME[datetime.month], datetime.year + 543)
    except:
        return ''


def format_abbr_date(datetime):
    try:
        return u'%d %s %d' % (datetime.day, datetime_constants.THAI_MONTH_ABBR_NAME[datetime.month], datetime.year + 543)
    except:
        return ''
"""


# TEXT #################################################################################################################

def get_excerpt(full_content, limit):
    excerpt = ''
    blocks = full_content.split(' ')
    for block in blocks:
        if len(excerpt + block) > limit:
            if limit - len(excerpt) > len(excerpt + block) - limit:
                excerpt += block + ' '

            return excerpt.strip(), full_content.strip() != excerpt.strip()
        else:
            excerpt += block + ' '

    if excerpt:
        return excerpt.strip(), full_content.strip() != excerpt.strip()

    return full_content[0:limit], full_content.strip() != full_content[0:limit]


# STORY ################################################################################################################

def clean_content(content):
    return content


# VALIDATION ###########################################################################################################

def check_email_format(email):
    from django.core.validators import email_re
    return bool(email_re.match(email))


# MISC #################################################################################################################

def split_filepath(path):
    (head, tail) = os.path.split(path)
    (root, ext) = os.path.splitext(tail)

    if ext and ext[0] == '.':
        ext = ext[1:]

    return head, root, ext


def extract_request_object(request_data, startswith):
    object = {}
    for request_key in request_data.keys():
        if request_key.startswith(startswith):
            key = request_key[request_key.find('[')+1:request_key.find(']')]
            data_key = request_key[request_key.rfind('[')+1:request_key.rfind(']')]

            if key not in object:
                object[key] = {}

            object[key][data_key] = request_data[request_key]

    return object