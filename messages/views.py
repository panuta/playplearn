from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from messages.utils import format_body
from postman.models import Message
from postman.utils import format_subject

from postman.views import _folder
from postman.views import view as postman_view, view_conversation as postman_view_conversation, reply as postman_reply
from postman.api import pm_write

from common import errors
from common.shortcuts import response_json_success, response_json_error_with_message
from domain.models import UserAccount


@login_required
def view_messages_inbox(request, option=None):
    return _folder(request, 'inbox', 'postman_inbox', option, 'messages/messages_inbox.html')


@login_required
def view_messages_sent(request, option=None):
    return _folder(request, 'sent', 'postman_sent', option, 'messages/messages_sent.html')


@login_required
def view_messages_trash(request, option=None):
    return _folder(request, 'trash', 'postman_trash', option, 'messages/messages_trash.html')


@login_required
def view_message(request, message_id):
    message = get_object_or_404(Message, pk=message_id)

    if message.thread_id:
        return postman_view_conversation(request, message.thread_id,
                                         template_name='messages/message.html',
                                         formatters=(format_subject, format_body))
    else:
        return postman_view(request, message_id,
                            template_name='messages/message.html',
                            formatters=(format_subject, format_body))


@login_required
def reply_message(request, message_id):
    return postman_reply(request, message_id,
                         template_name='messages/message.html',
                         success_url='%s#message-last' % reverse('view_message', args=[message_id]))


@require_POST
@login_required
def ajax_send_message(request):
    if not request.is_ajax():
        raise Http404

    recipient_id = request.POST.get('recipient')
    subject = request.POST.get('subject')
    body = request.POST.get('body')

    try:
        recipient = UserAccount.objects.get(pk=recipient_id)
    except UserAccount.DoesNotExist:
        return response_json_error_with_message('recipient-notfound', errors.MESSAGES_ERRORS)

    if not subject:
        return response_json_error_with_message('subject-empty', errors.MESSAGES_ERRORS)

    if not body:
        return response_json_error_with_message('body-empty', errors.MESSAGES_ERRORS)

    pm_write(request.user, recipient, subject, body)

    return response_json_success({

    })
