
from django import template
from django.utils.timezone import now

register = template.Library()

@register.filter
def daysuntil(from_datetime):
    return (from_datetime - now()).days


@register.filter
def timepast(from_datetime):
    return from_datetime < now()