from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.views.decorators.http import require_POST

from postman.api import pm_write

from common import errors
from common.shortcuts import response_json_success, response_json_error_with_message
from domain.models import UserAccount


def view_messages_inbox(request):
    pass


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
