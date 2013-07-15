# -*- encoding: utf-8 -*-

from django import template
from postman.models import Message

register = template.Library()


@register.assignment_tag
def first_message_in_thread(message):

    try:
        return Message.objects.filter(thread_id=message.thread_id).latest('sent_at')
    except Message.DoesNotExist:
        return message


@register.assignment_tag
def latest_message_in_thread(message):
    try:
        return Message.objects.filter(thread_id=message.thread_id).latest('sent_at')
    except Message.DoesNotExist:
        return message


@register.filter
def unread(message, user):
    if message.sender.id == user.id or message.read_at:
        return False
    else:
        return True