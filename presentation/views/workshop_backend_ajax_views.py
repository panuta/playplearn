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
from common.errors import WorkshopScheduleException
from common.shortcuts import response_json_success, response_json_error_with_message, response_json_error
from common.utilities import format_full_datetime, format_datetime_url_string

from domain import functions as domain_functions
from domain.models import WorkshopFeedback, Workshop, WorkshopPicture, Place

from reservation import functions as reservation_functions

from presentation.templatetags.presentation_tags import workshop_pictures_ordering_as_comma_separated, feedback_feelings_as_em
from reservation.models import Reservation


def _response_with_workshop_error(error_code):
    return response_json_error_with_message(error_code, errors.WORKSHOP_BACKEND_ERRORS)


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
            return _response_with_workshop_error('unauthorized')

    if workshop.is_status_wait_for_approval():
        return _response_with_workshop_error('edit-while-approving')

    domain_functions.save_workshop(workshop, request.POST)

    submit_action = request.POST.get('submit')
    if submit_action == 'approval':
        if workshop.is_status_draft():
            if domain_functions.is_workshop_outline_completed(workshop):
                domain_functions.submit_workshop(workshop)
            else:
                return _response_with_workshop_error('submit-before-complete')
        else:
            return _response_with_workshop_error('submit-not-draft')

    return response_json_success({
        'workshop_uid': workshop.uid,
        'is_completed': domain_functions.is_workshop_outline_completed(workshop),
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
            return _response_with_workshop_error('unauthorized')

    if workshop.is_status_wait_for_approval():
        return _response_with_workshop_error('edit-while-approving')

    if WorkshopPicture.objects.filter(workshop=workshop).count() > settings.WORKSHOP_MAXIMUM_PICTURE_NUMBER:
        return _response_with_workshop_error('file-numbers-exceeded')

    image_file = request.FILES['pictures[]']

    if image_file.size > settings.WORKSHOP_MAXIMUM_PICTURE_SIZE:
        return _response_with_workshop_error('file-size-exceeded')

    last_ordering = WorkshopPicture.objects.filter(workshop=workshop, mark_deleted=False) \
        .aggregate(Max('ordering'))['ordering__max']

    if not last_ordering:
        last_ordering = 0

    if workshop.is_status_draft() or workshop.is_status_ready_to_publish():
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
        return _response_with_workshop_error('picture-status-invalid')

    workshop_picture_url = get_thumbnailer(workshop_picture.image)['workshop_picture_small'].url

    return response_json_success({
        'is_completed': domain_functions.is_workshop_outline_completed(workshop),
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
        return _response_with_workshop_error('unauthorized')

    if workshop.is_status_wait_for_approval():
        return _response_with_workshop_error('edit-while-approving')

    try:
        workshop_picture = WorkshopPicture.objects.get(uid=picture_uid)
    except WorkshopPicture.DoesNotExist:
        return _response_with_workshop_error('picture-notfound')

    if workshop.is_status_draft() or workshop.is_status_ready_to_publish():
        workshop_picture.image.delete()
        workshop_picture.delete()

    elif workshop.is_status_published():
        workshop_picture.mark_deleted = True
        workshop_picture.save()
    else:
        return _response_with_workshop_error('picture-status-invalid')

    return response_json_success({
        'is_completed': domain_functions.is_workshop_outline_completed(workshop),
        'ordering': workshop_pictures_ordering_as_comma_separated(workshop),
    })


@require_GET
@login_required
def ajax_get_workshop_place(request):
    place_id = request.GET.get('place_id')

    try:
        place = Place.objects.get(pk=place_id, created_by=request.user)
    except Place.DoesNotExist:
        return _response_with_workshop_error('place-notfound')

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
        return _response_with_workshop_error('unauthorized')

    if not workshop.is_status_ready_to_publish():
        return _response_with_workshop_error('publish-status-invalid')

    try:
        schedule_datetime = datetime.datetime.strptime(request.POST.get('schedule_datetime'), '%Y-%m-%d-%H-%M')
    except ValueError:
        return _response_with_workshop_error('schedule-invalid')

    rightnow = now()

    if schedule_datetime < rightnow:
        return _response_with_workshop_error('schedule-past')
    elif (schedule_datetime - rightnow).days > settings.WORKSHOP_SCHEDULE_ALLOW_DAYS_IN_ADVANCE:
        return _response_with_workshop_error('schedule-far')

    try:
        schedule_price = int(request.POST.get('schedule_price'))
    except ValueError:
        schedule_price = workshop.default_price

    try:
        schedule_capacity = int(request.POST.get('schedule_capacity'))
    except ValueError:
        schedule_capacity = workshop.default_capacity

    try:
        schedule = reservation_functions.create_schedule(workshop, schedule_datetime, schedule_price, schedule_capacity)
    except WorkshopScheduleException, e:
        return _response_with_workshop_error(e.exception_code)

    domain_functions.publish_workshop(workshop)

    from django.template.loader import render_to_string

    return response_json_success({
        'workshop_url': '%s%s' % (settings.WEBSITE_URL, reverse('view_workshop_outline', args=[workshop.uid])),
        'workshop_html': render_to_string('workshop/backend/snippets/row_of_organize_workshop.html', {'workshop': workshop}),
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
        return _response_with_workshop_error('unauthorized')

    if not workshop.is_status_published():
        return _response_with_workshop_error('schedule-while-not-published')

    try:
        schedule_datetime = datetime.datetime.strptime(request.POST.get('schedule_datetime'), '%Y-%m-%d-%H-%M')
    except ValueError:
        return _response_with_workshop_error('schedule-invalid')

    rightnow = now()

    if schedule_datetime < rightnow:
        return _response_with_workshop_error('schedule-past')
    elif (schedule_datetime - rightnow).days > settings.WORKSHOP_SCHEDULE_ALLOW_DAYS_IN_ADVANCE:
        return _response_with_workshop_error('schedule-far')

    try:
        schedule_price = int(request.POST.get('schedule_price'))
    except ValueError:
        schedule_price = workshop.default_price

    try:
        schedule_capacity = int(request.POST.get('schedule_capacity'))
    except ValueError:
        schedule_capacity = workshop.default_capacity

    try:
        schedule = reservation_functions.create_schedule(workshop, schedule_datetime, schedule_price, schedule_capacity)
    except WorkshopScheduleException, e:
        return _response_with_workshop_error(e.exception_code)

    from common.templatetags.common_tags import schedule_datetime as format_schedule_datetime
    upcoming_schedule = workshop.get_upcoming_schedule()

    return response_json_success({
        'upcoming_schedule_datetime': format_schedule_datetime(upcoming_schedule),
        'upcoming_schedule_count': workshop.stats_upcoming_schedules(),
        'upcoming_participant_comfirmed': upcoming_schedule.seats_confirmed_and_paid(),
        'upcoming_participant_waiting': upcoming_schedule.seats_confirmed_and_wait_for_payment(),
    })


# WORKSHOP FEEDBACK ####################################################################################################

@require_GET
@login_required
def ajax_view_workshop_feedback(request):
    if not request.is_ajax():
        raise Http404

    reservation_code = request.GET.get('code')
    reservation = get_object_or_404(Reservation, code=reservation_code)

    if reservation.user != request.user and reservation.schedule.workshop.teacher != request.user:
        return _response_with_workshop_error('unauthorized')

    feedback = get_object_or_404(WorkshopFeedback, reservation=reservation)

    return response_json_success({
        'feelings': feedback_feelings_as_em(feedback),
        'content': linebreaks(feedback.content),
    })


@require_POST
@login_required
def ajax_add_workshop_feedback(request):
    if not request.is_ajax():
        raise Http404

    reservation_code = request.POST.get('code')
    reservation = get_object_or_404(Reservation, code=reservation_code)

    if reservation.user != request.user:
        return _response_with_workshop_error('unauthorized')

    try:
        WorkshopFeedback.objects.get(reservation=reservation)
    except WorkshopFeedback.DoesNotExist:
        pass
    else:
        return _response_with_workshop_error('feedback-existed')

    feeling_list = request.POST.getlist('feelings[]')
    content = request.POST.get('content', '')

    if not feeling_list and not content:
        return _response_with_workshop_error('feedback-empty')

    valid_feelings = []
    for feeling in feeling_list:
        if feeling in FEEDBACK_FEELING_MAP:
            valid_feelings.append(feeling)

    WorkshopFeedback.objects.create(
        reservation=reservation,
        content=content,
        feelings=','.join(valid_feelings),
    )

    return response_json_success()


@require_POST
@login_required
def ajax_delete_workshop_feedback(request):
    if not request.is_ajax():
        raise Http404

    reservation_code = request.POST.get('code')
    reservation = get_object_or_404(Reservation, code=reservation_code)

    if reservation.user != request.user:
        return _response_with_workshop_error('unauthorized')

    try:
        feedback = WorkshopFeedback.objects.get(reservation=reservation)
    except WorkshopFeedback.DoesNotExist:
        return _response_with_workshop_error('feedback-notfound')

    feedback.delete()
    return response_json_success()


@require_POST
@login_required
def ajax_set_workshop_feedback_visibility(request):
    if not request.is_ajax():
        raise Http404

    visibility = request.POST.get('visibility')
    visibility = True if visibility == 'true' else False

    feedback_id = request.POST.get('feedback_id')
    feedback = get_object_or_404(WorkshopFeedback, pk=feedback_id)

    if feedback.reservation.schedule.workshop.teacher != request.user:
        return _response_with_workshop_error('unauthorized')

    feedback.is_visible = visibility
    feedback.save()

    return response_json_success({
        'is_visible': feedback.is_visible,
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