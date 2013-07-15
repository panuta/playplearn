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
from common.constants.course import COURSE_ENROLLMENT_STATUS_MAP, COURSE_ENROLLMENT_PAYMENT_STATUS_MAP
from common.constants.currency import CURRENCY_CODE_MAP
from common.constants.feedback import FEEDBACK_FEELING_MAP
from common.constants.payment import BANK_ACCOUNT_MAP
from common.shortcuts import response_json_success, response_json_error_with_message, response_json_error
from common.utilities import format_full_datetime, format_datetime_string

from domain import functions as domain_function
from domain.models import CourseFeedback, CourseEnrollment, Course, CourseSchedule, CoursePicture, EditingCourse, Place, CourseEnrollmentPaymentNotify


# COURSE ###############################################################################################################
from presentation.templatetags.presentation_tags import course_picture_ordering_as_comma_separated


@require_POST
@login_required
def ajax_save_course(request):
    if not request.is_ajax():
        raise Http404

    course_uid = request.POST.get('uid')

    try:
        course = Course.objects.get(uid=course_uid)
    except Course.DoesNotExist:
        course = Course.objects.create(
            uid=course_uid,
            teacher=request.user,
            status='DRAFT',
        )
    else:
        if course.teacher != request.user:
            return response_json_error_with_message('unauthorized', errors.COURSE_MODIFICATION_ERRORS)

    domain_function.save_course(course, request.POST)

    submit_action = request.POST.get('submit')

    if submit_action == 'approval':
        if course.status == 'DRAFT':
            if domain_function.is_course_outline_completed(course):
                course.status = 'WAIT_FOR_APPROVAL'
                course.save()
            else:
                return response_json_error_with_message('course-incomplete', errors.COURSE_MODIFICATION_ERRORS)
        else:
            return response_json_error_with_message('status-no-ready-to-submit', errors.COURSE_MODIFICATION_ERRORS)

    return response_json_success({
        'course_uid': course.uid,
        'is_completed': domain_function.is_course_outline_completed(course),
        'preview_url': reverse('view_course_outline', args=[course.uid]),
        'edit_url': reverse('edit_course', args=[course.uid]),
    })


@require_POST
@login_required
def ajax_upload_course_cover(request):
    if not request.is_ajax():
        raise Http404

    course_uid = request.POST.get('uid')

    try:
        course = Course.objects.get(uid=course_uid)
    except Course.DoesNotExist:
        course = Course.objects.create(
            uid=course_uid,
            teacher=request.user,
            status='DRAFT',
        )
    else:
        if course.teacher != request.user:
            return response_json_error_with_message('unauthorized', errors.COURSE_MODIFICATION_ERRORS)

    cover_file = request.FILES['cover']

    if cover_file.size > settings.COURSE_COVER_MAXIMUM_SIZE:
        return response_json_error('file-size-exceeded')

    if course.status == 'DRAFT':
        editing_course = course
    elif course.status in ('PUBLISHED', 'WAIT_FOR_APPROVAL', 'READY_TO_PUBLISH'):
        editing_course, _ = EditingCourse.objects.get_or_create(course=course)
    else:
        return response_json_error_with_message('status-invalid', errors.COURSE_MODIFICATION_ERRORS)

    if editing_course.cover:
        editing_course.cover.delete()

    try:
        editing_course.cover = cover_file
        editing_course.save()
        cover_url = get_thumbnailer(editing_course.cover)['course_cover_small'].url
    except InvalidImageFormatError:
        return response_json_error_with_message('file-type-invalid', errors.COURSE_MODIFICATION_ERRORS)

    return response_json_success({
        'is_completed': domain_function.is_course_outline_completed(course),
        'cover_url': cover_url,
        'cover_filename': editing_course.cover.name,
    })


@require_POST
@login_required
def ajax_upload_course_picture(request):
    course_uid = request.POST.get('uid')

    try:
        course = Course.objects.get(uid=course_uid)
    except Course.DoesNotExist:
        course = Course.objects.create(
            uid=course_uid,
            teacher=request.user,
            status='DRAFT',
        )
    else:
        if course.teacher != request.user:
            return response_json_error_with_message('unauthorized', errors.COURSE_MODIFICATION_ERRORS)

    if CoursePicture.objects.filter(course=course).count() > settings.COURSE_PICTURE_MAXIMUM_NUMBER:
        return response_json_error_with_message('file-number-exceeded', errors.COURSE_MODIFICATION_ERRORS)

    image_file = request.FILES['pictures[]']

    if image_file.size > settings.COURSE_PICTURE_MAXIMUM_SIZE:
        return response_json_error_with_message('file-size-exceeded', errors.COURSE_MODIFICATION_ERRORS)

    last_ordering = CoursePicture.objects.filter(course=course, mark_deleted=False) \
        .aggregate(Max('ordering'))['ordering__max']

    if not last_ordering:
        last_ordering = 0

    if course.status in ('DRAFT', 'WAIT_FOR_APPROVAL', 'READY_TO_PUBLISH'):
        course_picture = CoursePicture.objects.create(
            course=course,
            image=image_file,
            ordering=last_ordering+1,
            is_visible=True,
        )

    elif course.status == 'PUBLISHED':
        course_picture = CoursePicture.objects.create(
            course=course,
            image=image_file,
            ordering=last_ordering+1,
            mark_added=True,
            is_visible=False,
        )

    else:
        return response_json_error_with_message('status-invalid', errors.COURSE_MODIFICATION_ERRORS)

    course_picture_url = get_thumbnailer(course_picture.image)['course_picture_small'].url

    return response_json_success({
        'is_completed': domain_function.is_course_outline_completed(course),
        'ordering': course_picture_ordering_as_comma_separated(course),
        'picture_uid': course_picture.uid,
        'picture_url': course_picture_url,
    })


"""
@require_POST
@login_required
def ajax_reorder_course_picture(request):
    if not request.is_ajax():
        raise Http404

    course_uid = request.POST.get('uid')
    course = get_object_or_404(Course, uid=course_uid)

    if course.teacher != request.user:
        return response_json_error_with_message('unauthorized', errors.COURSE_MODIFICATION_ERRORS)

    ordering = 1
    pictures_ordering = []
    for picture_uid in request.POST.get('ordering').split(','):
        try:
            course_picture = CoursePicture.objects.get(course=course, uid=picture_uid)
        except CoursePicture.DoesNotExist:
            pass
        else:
            pictures_ordering.append({'picture': course_picture, 'ordering': ordering})
            ordering += 1

    if course.status in ('DRAFT', 'WAIT_FOR_APPROVAL', 'READY_TO_PUBLISH'):
        for picture_ordering in pictures_ordering:
            picture_ordering['picture'].ordering = picture_ordering['ordering']
            picture_ordering['picture'].save()

    elif course.status == 'PUBLISHED':
        CoursePictureEditingOrdering.objects.filter(picture__course=course).delete()
        for picture_ordering in pictures_ordering:
            CoursePictureEditingOrdering.objects.create(picture=picture_ordering['picture'], ordering=picture_ordering['ordering'])

    else:
        return response_json_error_with_message('status-invalid', errors.COURSE_MODIFICATION_ERRORS)

    return response_json_success({
        'is_completed': domain_function.is_course_outline_completed(course),
        'ordering': course_picture_ordering_as_comma_separated(course),
    })
"""


@require_POST
@login_required
def ajax_delete_course_picture(request):
    if not request.is_ajax():
        raise Http404

    course_uid = request.POST.get('uid')
    course = get_object_or_404(Course, uid=course_uid)

    picture_uid = request.POST.get('picture_uid')

    if course.teacher != request.user:
        return response_json_error_with_message('unauthorized', errors.COURSE_MODIFICATION_ERRORS)

    try:
        course_picture = CoursePicture.objects.get(uid=picture_uid)
    except CoursePicture.DoesNotExist:
        return response_json_error_with_message('picture-notfound', errors.COURSE_MODIFICATION_ERRORS)


    if course.status in ('DRAFT', 'WAIT_FOR_APPROVAL', 'READY_TO_PUBLISH'):
        course_picture.image.delete()
        course_picture.delete()

    elif course.status == 'PUBLISHED':
        course_picture.mark_deleted = True
        course_picture.save()

    else:
        return response_json_error_with_message('status-invalid', errors.COURSE_MODIFICATION_ERRORS)

    return response_json_success({
        'is_completed': domain_function.is_course_outline_completed(course),
        'ordering': course_picture_ordering_as_comma_separated(course),
    })


@require_GET
@login_required
def ajax_get_course_place(request):
    place_id = request.GET.get('place_id')

    try:
        place = Place.objects.get(pk=place_id, created_by=request.user)
    except Place.DoesNotExist:
        return response_json_error_with_message('place-notfound', errors.COURSE_MODIFICATION_ERRORS)

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
def ajax_publish_course(request):
    if not request.is_ajax():
        raise Http404

    course_uid = request.POST.get('uid')

    course = get_object_or_404(Course, uid=course_uid)

    if course.teacher != request.user:
        return response_json_error_with_message('unauthorized', errors.COURSE_MODIFICATION_ERRORS)

    if course.status != 'READY_TO_PUBLISH':
        return response_json_error_with_message('status-no-ready-to-publish', errors.COURSE_MODIFICATION_ERRORS)

    try:
        datetime_data = '%s-%s' % (request.POST.get('schedule_date'), request.POST.get('schedule_time'))
        schedule_datetime = datetime.datetime.strptime(datetime_data, '%Y-%m-%d-%H-%M')
    except ValueError:
        return response_json_error_with_message('input-invalid', errors.COURSE_MODIFICATION_ERRORS)

    CourseSchedule.objects.create(course=course, start_datetime=schedule_datetime)

    rightnow = now()

    course.status = 'PUBLISHED'
    course.first_published = rightnow
    course.last_scheduled = rightnow
    course.save()

    CourseOutlineMedia.objects.filter(course=course).update(is_visible=True)

    if course.place.is_userdefined:
        course.place.is_visible = True
        course.place.save()

    messages.success(request, 'Successfully publish your course. You can now promote the course here.')

    return response_json_success({
        'redirect_url': reverse('manage_course_promote', args=[course.uid]),
    })


# COURSE SCHEDULE ######################################################################################################

@require_POST
@login_required
def ajax_add_course_schedule(request):
    if not request.is_ajax():
        raise Http404

    course_uid = request.POST.get('uid')

    course = get_object_or_404(Course, uid=course_uid)

    if course.teacher != request.user:
        return response_json_error_with_message('unauthorized', errors.COURSE_MODIFICATION_ERRORS)

    if course.status != 'PUBLISHED':
        return response_json_error_with_message('status-no-ready-to-publish', errors.COURSE_MODIFICATION_ERRORS)

    try:
        schedule_datetime = parse_datetime(
            '%s %s' % (request.POST.get('schedule_date'), request.POST.get('schedule_time')))
    except ValueError:
        return response_json_error_with_message('input-invalid', errors.COURSE_MODIFICATION_ERRORS)

    rightnow = now()

    if schedule_datetime < rightnow:
        return response_json_error_with_message('schedule-past', errors.COURSE_MODIFICATION_ERRORS)
    elif (schedule_datetime - rightnow).days > settings.SCHEDULE_ADD_DAYS_IN_ADVANCE:
        return response_json_error_with_message('schedule-future', errors.COURSE_MODIFICATION_ERRORS)

    schedule, created = CourseSchedule.objects.get_or_create(course=course, start_datetime=schedule_datetime)

    if not created:
        return response_json_error_with_message('schedule-duplicated', errors.COURSE_MODIFICATION_ERRORS)

    course.last_scheduled = rightnow
    course.save()

    return response_json_success({
        'manage_class_url': reverse('manage_course_class',
                                    args=[course.uid, format_datetime_string(schedule.start_datetime)])
    })


# COURSE FEEDBACK ######################################################################################################

@require_GET
@login_required
def ajax_view_course_feedback(request):
    if not request.is_ajax():
        raise Http404

    enrollment_code = request.GET.get('code')
    enrollment = get_object_or_404(CourseEnrollment, code=enrollment_code)

    if enrollment.student != request.user and enrollment.schedule.course.teacher != request.user:
        return response_json_error_with_message('unauthorized', errors.COURSE_FEEDBACK_ERRORS)

    feedback = get_object_or_404(CourseFeedback, enrollment=enrollment)

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
def ajax_add_course_feedback(request):
    if not request.is_ajax():
        raise Http404

    enrollment_code = request.POST.get('code')
    enrollment = get_object_or_404(CourseEnrollment, code=enrollment_code)

    if enrollment.student != request.user:
        return response_json_error_with_message('unauthorized', errors.COURSE_FEEDBACK_ERRORS)

    try:
        CourseFeedback.objects.get(enrollment=enrollment)
    except CourseFeedback.DoesNotExist:
        pass
    else:
        return response_json_error_with_message('existed', errors.COURSE_FEEDBACK_ERRORS)

    feeling_list = request.POST.getlist('feelings[]')
    content = request.POST.get('content', '')

    if not feeling_list and not content:
        return response_json_error_with_message('empty', errors.COURSE_FEEDBACK_ERRORS)

    valid_feelings = []
    for feeling in feeling_list:
        if feeling in FEEDBACK_FEELING_MAP:
            valid_feelings.append(feeling)

    CourseFeedback.objects.create(
        enrollment=enrollment,
        content=content,
        feelings=','.join(valid_feelings),
    )

    return response_json_success()


@require_POST
@login_required
def ajax_delete_course_feedback(request):
    if not request.is_ajax():
        raise Http404

    enrollment_code = request.POST.get('code')
    enrollment = get_object_or_404(CourseEnrollment, code=enrollment_code)

    if enrollment.student != request.user:
        return response_json_error_with_message('unauthorized', errors.COURSE_FEEDBACK_ERRORS)

    try:
        feedback = CourseFeedback.objects.get(enrollment=enrollment)
    except CourseFeedback.DoesNotExist:
        return response_json_error_with_message('deleted', errors.COURSE_FEEDBACK_ERRORS)

    feedback.delete()
    return response_json_success()


@require_POST
@login_required
def ajax_set_course_feedback_public(request):
    if not request.is_ajax():
        raise Http404

    feedback_id = request.POST.get('feedback_id')
    feedback = get_object_or_404(CourseFeedback, pk=feedback_id)

    if feedback.enrollment.schedule.course.teacher != request.user:
        return response_json_error_with_message('unauthorized', errors.COURSE_MODIFICATION_ERRORS)

    feedback.is_public = not feedback.is_public
    feedback.save()

    return response_json_success({
        'is_public': feedback.is_public,
    })


@require_POST
@login_required
def ajax_set_course_feedback_promoted(request):
    if not request.is_ajax():
        raise Http404

    feedback_id = request.POST.get('feedback_id')
    feedback = get_object_or_404(CourseFeedback, pk=feedback_id)

    if feedback.enrollment.schedule.course.teacher != request.user:
        return response_json_error_with_message('unauthorized', errors.COURSE_MODIFICATION_ERRORS)

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
        enrollment = CourseEnrollment.objects.get(code=code)
    except CourseEnrollment.DoesNotExist:
        raise Http404

    course = enrollment.schedule.course
    return response_json_success({
        'title': course.title,
        'teacher_name': course.teacher.name,
        'schedule_datetime': format_full_datetime(enrollment.schedule.start_datetime),
        'amount': '%.0f %s' % (enrollment.total, CURRENCY_CODE_MAP[str(course.price_unit)]['name']),
        'status': COURSE_ENROLLMENT_STATUS_MAP[str(enrollment.status)]['name'],
        'payment_status': COURSE_ENROLLMENT_PAYMENT_STATUS_MAP[str(enrollment.payment_status)]['name'],
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
        enrollment = CourseEnrollment.objects.get(code=code)
    except CourseEnrollment.DoesNotExist:
        return response_json_error_with_message('enrollment-notfound', errors.COURSE_ENROLLMENT_ERRORS)

    if CourseEnrollmentPaymentNotify.objects.filter(enrollment=enrollment).exists():
        return response_json_error_with_message('payment-notify-duplicate', errors.COURSE_ENROLLMENT_ERRORS)

    bank = request.POST.get('bank', '')
    amount = request.POST.get('amount', '')
    date = request.POST.get('date', '')
    time_hour = request.POST.get('time_hour', '')
    time_minute = request.POST.get('time_minute', '')
    remark = request.POST.get('remark', '')

    if not bank or bank not in BANK_ACCOUNT_MAP:
        return response_json_error_with_message('payment-notify-bank-invalid', errors.COURSE_ENROLLMENT_ERRORS)

    try:
        amount = int(amount)
        if amount < 0:
            raise ValueError
    except ValueError:
        return response_json_error_with_message('payment-notify-amount-invalid', errors.COURSE_ENROLLMENT_ERRORS)

    try:
        datetime_data = '%s-%s-%s' % (date, time_hour, time_minute)
        transfered_on = datetime.datetime.strptime(datetime_data, '%Y-%m-%d-%H-%M')
    except ValueError:
        return response_json_error_with_message('input-invalid', errors.COURSE_MODIFICATION_ERRORS)

    CourseEnrollmentPaymentNotify.objects.create(
        enrollment=enrollment,
        bank=bank,
        amount=amount,
        transfered_on=transfered_on,
        remark=remark,
    )

    return response_json_success()