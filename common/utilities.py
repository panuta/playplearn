# -*- encoding: utf-8 -*-

import os

from common.constants import datetime as datetime_constants

# DATE & TIME ##########################################################################################################

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


# STORY ################################################################################################################

def clean_content(content):
    return content


# MISC #################################################################################################################

def split_filepath(path):
    (head, tail) = os.path.split(path)
    (root, ext) = os.path.splitext(tail)

    if ext and ext[0] == '.':
        ext = ext[1:]

    return head, root, ext