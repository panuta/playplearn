# -*- encoding: utf-8 -*-

import datetime
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Max
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
from django.utils.html import linebreaks
from django.utils.timezone import now
from django.views.decorators.http import require_POST, require_GET
from easy_thumbnails.exceptions import InvalidImageFormatError
from easy_thumbnails.files import get_thumbnailer

from common import errors
from common.constants.workshop import WORKSHOP_ENROLLMENT_STATUS_MAP, WORKSHOP_ENROLLMENT_PAYMENT_STATUS_MAP
from common.constants.currency import CURRENCY_CODE_MAP
from common.constants.feedback import FEEDBACK_FEELING_MAP
from common.constants.payment import BANK_ACCOUNT_MAP
from common.shortcuts import response_json_success, response_json_error_with_message, response_json_error
from common.utilities import format_full_datetime, format_datetime_string

from domain import functions as workshop_functions
from domain.models import WorkshopFeedback, Workshop, WorkshopPicture, Place

from presentation.templatetags.presentation_tags import workshop_pictures_ordering_as_comma_separated


# WORKSHOP #############################################################################################################

@require_POST
@login_required
def ajax_save_workshop(request):
    if not request.is_ajax():
        raise Http404

    workshop_uid = request.POST.get('uid')

    try:
        workshop = Workshop.objects.get(uid=workshop_uid)
    except Workshop.DoesNotExist:
        workshop = Workshop.objects.create(
            uid=workshop_uid,
            teacher=request.user,
            status=Workshop.STATUS_DRAFT,
        )
    else:
        if workshop.teacher != request.user:
            return response_json_error_with_message('unauthorized', errors.WORKSHOP_MODIFICATION_ERRORS)

    if workshop.is_status_wait_for_approval():
        return response_json_error_with_message('edit-while-approving', errors.WORKSHOP_MODIFICATION_ERRORS)

    workshop_functions.save_workshop(workshop, request.POST)

    submit_action = request.POST.get('submit')

    if submit_action == 'approval':
        if workshop.is_status_draft():
            if workshop_functions.is_workshop_outline_completed(workshop):
                workshop.status = Workshop.STATUS_WAIT_FOR_APPROVAL
                workshop.save()
            else:
                return response_json_error_with_message('workshop-incomplete', errors.WORKSHOP_MODIFICATION_ERRORS)
        else:
            return response_json_error_with_message('status-no-ready-to-submit', errors.WORKSHOP_MODIFICATION_ERRORS)

    return response_json_success({
        'workshop_uid': workshop.uid,
        'is_completed': workshop_functions.is_workshop_outline_completed(workshop),
        'preview_url': reverse('view_workshop_outline', args=[workshop.uid]),
        'edit_url': reverse('edit_workshop', args=[workshop.uid]),
    })


@require_POST
@login_required
def ajax_upload_workshop_picture(request):
    workshop_uid = request.POST.get('uid')

    try:
        workshop = Workshop.objects.get(uid=workshop_uid)
    except Workshop.DoesNotExist:
        workshop = Workshop.objects.create(
            uid=workshop_uid,
            teacher=request.user,
            status=Workshop.STATUS_DRAFT,
        )
    else:
        if workshop.teacher != request.user:
            return response_json_error_with_message('unauthorized', errors.WORKSHOP_MODIFICATION_ERRORS)

    if workshop.is_status_wait_for_approval():
        return response_json_error_with_message('edit-while-approving', errors.WORKSHOP_MODIFICATION_ERRORS)

    if WorkshopPicture.objects.filter(workshop=workshop).count() > settings.WORKSHOP_MAXIMUM_PICTURE_NUMBER:
        return response_json_error_with_message('file-number-exceeded', errors.WORKSHOP_MODIFICATION_ERRORS)

    image_file = request.FILES['pictures[]']

    if image_file.size > settings.WORKSHOP_MAXIMUM_PICTURE_SIZE:
        return response_json_error_with_message('file-size-exceeded', errors.WORKSHOP_MODIFICATION_ERRORS)

    last_ordering = WorkshopPicture.objects.filter(workshop=workshop, mark_deleted=False) \
        .aggregate(Max('ordering'))['ordering__max']

    if not last_ordering:
        last_ordering = 0

    if workshop.status in (Workshop.STATUS_DRAFT, Workshop.STATUS_WAIT_FOR_APPROVAL, Workshop.STATUS_READY_TO_PUBLISH):
        workshop_picture = WorkshopPicture.objects.create(
            workshop=workshop,
            image=image_file,
            ordering=last_ordering+1,
            is_visible=True,
        )

    elif workshop.is_status_published():
        workshop_picture = WorkshopPicture.objects.create(
            workshop=workshop,
            image=image_file,
            ordering=last_ordering+1,
            mark_added=True,
            is_visible=False,
        )

    else:
        return response_json_error_with_message('status-invalid', errors.WORKSHOP_MODIFICATION_ERRORS)

    workshop_picture_url = get_thumbnailer(workshop_picture.image)['workshop_picture_small'].url

    return response_json_success({
        'is_completed': workshop_functions.is_workshop_outline_completed(workshop),
        'ordering': workshop_pictures_ordering_as_comma_separated(workshop),
        'picture_uid': workshop_picture.uid,
        'picture_url': workshop_picture_url,
    })


@require_POST
@login_required
def ajax_delete_workshop_picture(request):
    if not request.is_ajax():
        raise Http404

    workshop_uid = request.POST.get('uid')
    workshop = get_object_or_404(Workshop, uid=workshop_uid)

    picture_uid = request.POST.get('picture_uid')

    if workshop.teacher != request.user:
        return response_json_error_with_message('unauthorized', errors.WORKSHOP_MODIFICATION_ERRORS)

    if workshop.is_status_wait_for_approval():
        return response_json_error_with_message('edit-while-approving', errors.WORKSHOP_MODIFICATION_ERRORS)

    try:
        workshop_picture = WorkshopPicture.objects.get(uid=picture_uid)
    except WorkshopPicture.DoesNotExist:
        return response_json_error_with_message('picture-notfound', errors.WORKSHOP_MODIFICATION_ERRORS)

    if workshop.status in (Workshop.STATUS_DRAFT, Workshop.STATUS_WAIT_FOR_APPROVAL, Workshop.STATUS_READY_TO_PUBLISH):
        workshop_picture.image.delete()
        workshop_picture.delete()

    elif workshop.is_status_published():
        workshop_picture.mark_deleted = True
        workshop_picture.save()

    else:
        return response_json_error_with_message('status-invalid', errors.WORKSHOP_MODIFICATION_ERRORS)

    return response_json_success({
        'is_completed': workshop_functions.is_workshop_outline_completed(workshop),
        'ordering': workshop_pictures_ordering_as_comma_separated(workshop),
    })


@require_GET
@login_required
def ajax_get_workshop_place(request):
    place_id = request.GET.get('place_id')

    try:
        place = Place.objects.get(pk=place_id, created_by=request.user)
    except Place.DoesNotExist:
        return response_json_error_with_message('place-notfound', errors.WORKSHOP_MODIFICATION_ERRORS)

    return response_json_success({
        'id': place.id,
        'name': place.name,
        'address': place.address,
        'province_code': place.province_code,
        'direction': place.direction,
        'latlng': place.latlng,
    })


@require_POST
@login_required
def ajax_publish_workshop(request):
    if not request.is_ajax():
        raise Http404

    workshop_uid = request.POST.get('uid')

    workshop = get_object_or_404(Workshop, uid=workshop_uid)

    if workshop.teacher != request.user:
        return response_json_error_with_message('unauthorized', errors.WORKSHOP_MODIFICATION_ERRORS)

    if workshop.status != 'READY_TO_PUBLISH':
        return response_json_error_with_message('status-no-ready-to-publish', errors.WORKSHOP_MODIFICATION_ERRORS)

    try:
        datetime_data = '%s-%s' % (request.POST.get('schedule_date'), request.POST.get('schedule_time'))
        schedule_datetime = datetime.datetime.strptime(datetime_data, '%Y-%m-%d-%H-%M')
    except ValueError:
        return response_json_error_with_message('input-invalid', errors.WORKSHOP_MODIFICATION_ERRORS)

    WorkshopSchedule.objects.create(workshop=workshop, start_datetime=schedule_datetime)

    rightnow = now()

    workshop.status = 'PUBLISHED'
    workshop.first_published = rightnow
    workshop.last_scheduled = rightnow
    workshop.save()

    WorkshopOutlineMedia.objects.filter(workshop=workshop).update(is_visible=True)

    if workshop.place.is_userdefined:
        workshop.place.is_visible = True
        workshop.place.save()

    messages.success(request, 'Successfully publish your workshop. You can now promote the workshop here.')

    return response_json_success({
        'redirect_url': reverse('manage_workshop_promote', args=[workshop.uid]),
    })


# WORKSHOP SCHEDULE ####################################################################################################

@require_POST
@login_required
def ajax_add_workshop_schedule(request):
    if not request.is_ajax():
        raise Http404

    workshop_uid = request.POST.get('uid')

    workshop = get_object_or_404(Workshop, uid=workshop_uid)

    if workshop.teacher != request.user:
        return response_json_error_with_message('unauthorized', errors.WORKSHOP_MODIFICATION_ERRORS)

    if workshop.status != 'PUBLISHED':
        return response_json_error_with_message('status-no-ready-to-publish', errors.WORKSHOP_MODIFICATION_ERRORS)

    try:
        schedule_datetime = parse_datetime(
            '%s %s' % (request.POST.get('schedule_date'), request.POST.get('schedule_time')))
    except ValueError:
        return response_json_error_with_message('input-invalid', errors.WORKSHOP_MODIFICATION_ERRORS)

    rightnow = now()

    if schedule_datetime < rightnow:
        return response_json_error_with_message('schedule-past', errors.WORKSHOP_MODIFICATION_ERRORS)
    elif (schedule_datetime - rightnow).days > settings.SCHEDULE_ADD_DAYS_IN_ADVANCE:
        return response_json_error_with_message('schedule-future', errors.WORKSHOP_MODIFICATION_ERRORS)

    schedule, created = WorkshopSchedule.objects.get_or_create(workshop=workshop, start_datetime=schedule_datetime)

    if not created:
        return response_json_error_with_message('schedule-duplicated', errors.WORKSHOP_MODIFICATION_ERRORS)

    workshop.last_scheduled = rightnow
    workshop.save()

    return response_json_success({
        'manage_class_url': reverse('manage_workshop_class',
                                    args=[workshop.uid, format_datetime_string(schedule.start_datetime)])
    })


# WORKSHOP FEEDBACK ####################################################################################################

@require_GET
@login_required
def ajax_view_workshop_feedback(request):
    if not request.is_ajax():
        raise Http404

    enrollment_code = request.GET.get('code')
    enrollment = get_object_or_404(WorkshopEnrollment, code=enrollment_code)

    if enrollment.student != request.user and enrollment.schedule.workshop.teacher != request.user:
        return response_json_error_with_message('unauthorized', errors.WORKSHOP_FEEDBACK_ERRORS)

    feedback = get_object_or_404(WorkshopFeedback, enrollment=enrollment)

    feeling_names = []
    for feeling in feedback.feelings.split(','):
        if feeling in FEEDBACK_FEELING_MAP:
            feeling_names.append(FEEDBACK_FEELING_MAP[feeling]['name'])

    return response_json_success({
        'feelings': feeling_names,
        'content': linebreaks(feedback.content),
    })


@require_POST
@login_required
def ajax_add_workshop_feedback(request):
    if not request.is_ajax():
        raise Http404

    enrollment_code = request.POST.get('code')
    enrollment = get_object_or_404(WorkshopEnrollment, code=enrollment_code)

    if enrollment.student != request.user:
        return response_json_error_with_message('unauthorized', errors.WORKSHOP_FEEDBACK_ERRORS)

    try:
        WorkshopFeedback.objects.get(enrollment=enrollment)
    except WorkshopFeedback.DoesNotExist:
        pass
    else:
        return response_json_error_with_message('existed', errors.WORKSHOP_FEEDBACK_ERRORS)

    feeling_list = request.POST.getlist('feelings[]')
    content = request.POST.get('content', '')

    if not feeling_list and not content:
        return response_json_error_with_message('empty', errors.WORKSHOP_FEEDBACK_ERRORS)

    valid_feelings = []
    for feeling in feeling_list:
        if feeling in FEEDBACK_FEELING_MAP:
            valid_feelings.append(feeling)

    WorkshopFeedback.objects.create(
        enrollment=enrollment,
        content=content,
        feelings=','.join(valid_feelings),
    )

    return response_json_success()


@require_POST
@login_required
def ajax_delete_workshop_feedback(request):
    if not request.is_ajax():
        raise Http404

    enrollment_code = request.POST.get('code')
    enrollment = get_object_or_404(WorkshopEnrollment, code=enrollment_code)

    if enrollment.student != request.user:
        return response_json_error_with_message('unauthorized', errors.WORKSHOP_FEEDBACK_ERRORS)

    try:
        feedback = WorkshopFeedback.objects.get(enrollment=enrollment)
    except WorkshopFeedback.DoesNotExist:
        return response_json_error_with_message('deleted', errors.WORKSHOP_FEEDBACK_ERRORS)

    feedback.delete()
    return response_json_success()


@require_POST
@login_required
def ajax_set_workshop_feedback_public(request):
    if not request.is_ajax():
        raise Http404

    feedback_id = request.POST.get('feedback_id')
    feedback = get_object_or_404(WorkshopFeedback, pk=feedback_id)

    if feedback.enrollment.schedule.workshop.teacher != request.user:
        return response_json_error_with_message('unauthorized', errors.WORKSHOP_MODIFICATION_ERRORS)

    feedback.is_public = not feedback.is_public
    feedback.save()

    return response_json_success({
        'is_public': feedback.is_public,
    })


@require_POST
@login_required
def ajax_set_workshop_feedback_promoted(request):
    if not request.is_ajax():
        raise Http404

    feedback_id = request.POST.get('feedback_id')
    feedback = get_object_or_404(WorkshopFeedback, pk=feedback_id)

    if feedback.enrollment.schedule.workshop.teacher != request.user:
        return response_json_error_with_message('unauthorized', errors.WORKSHOP_MODIFICATION_ERRORS)

    feedback.is_promoted = not feedback.is_promoted
    feedback.save()

    return response_json_success({
        'is_promoted': feedback.is_promoted,
    })


# ENROLLMENT ###########################################################################################################

@require_GET
@login_required
def ajax_view_enrollment_details(request):
    if not request.is_ajax():
        raise Http404

    code = request.GET.get('code')

    try:
        enrollment = WorkshopEnrollment.objects.get(code=code)
    except WorkshopEnrollment.DoesNotExist:
        raise Http404

    workshop = enrollment.schedule.workshop
    return response_json_success({
        'title': workshop.title,
        'teacher_name': workshop.teacher.name,
        'schedule_datetime': format_full_datetime(enrollment.schedule.start_datetime),
        'amount': '%.0f %s' % (enrollment.total, CURRENCY_CODE_MAP[str(workshop.price_unit)]['name']),
        'status': WORKSHOP_ENROLLMENT_STATUS_MAP[str(enrollment.status)]['name'],
        'payment_status': WORKSHOP_ENROLLMENT_PAYMENT_STATUS_MAP[str(enrollment.payment_status)]['name'],
        'reserved_on': format_full_datetime(enrollment.created),
        'print_url': '',
    })


@require_POST
@login_required
def ajax_notify_enrollment_payment(request):
    if not request.is_ajax():
        raise Http404

    code = request.POST.get('code')

    try:
        enrollment = WorkshopEnrollment.objects.get(code=code)
    except WorkshopEnrollment.DoesNotExist:
        return response_json_error_with_message('enrollment-notfound', errors.WORKSHOP_ENROLLMENT_ERRORS)

    if WorkshopEnrollmentPaymentNotify.objects.filter(enrollment=enrollment).exists():
        return response_json_error_with_message('payment-notify-duplicate', errors.WORKSHOP_ENROLLMENT_ERRORS)

    bank = request.POST.get('bank', '')
    amount = request.POST.get('amount', '')
    date = request.POST.get('date', '')
    time_hour = request.POST.get('time_hour', '')
    time_minute = request.POST.get('time_minute', '')
    remark = request.POST.get('remark', '')

    if not bank or bank not in BANK_ACCOUNT_MAP:
        return response_json_error_with_message('payment-notify-bank-invalid', errors.WORKSHOP_ENROLLMENT_ERRORS)

    try:
        amount = int(amount)
        if amount < 0:
            raise ValueError
    except ValueError:
        return response_json_error_with_message('payment-notify-amount-invalid', errors.WORKSHOP_ENROLLMENT_ERRORS)

    try:
        datetime_data = '%s-%s-%s' % (date, time_hour, time_minute)
        transfered_on = datetime.datetime.strptime(datetime_data, '%Y-%m-%d-%H-%M')
    except ValueError:
        return response_json_error_with_message('input-invalid', errors.WORKSHOP_MODIFICATION_ERRORS)

    WorkshopEnrollmentPaymentNotify.objects.create(
        enrollment=enrollment,
        bank=bank,
        amount=amount,
        transfered_on=transfered_on,
        remark=remark,
    )

    return response_json_success()