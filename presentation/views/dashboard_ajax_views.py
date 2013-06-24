import datetime
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
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
from common.shortcuts import response_json_success, response_json_error_with_message, response_json_error
from common.utilities import format_full_datetime, format_datetime_string

from domain import functions as domain_function
from domain.models import CourseFeedback, CourseEnrollment, Course, CourseSchedule, CourseOutlineMedia, EditingCourse, CoursePicture, EditingCourseOutlineMedia, EditingCoursePicture


# COURSE ###############################################################################################################

@require_POST
@login_required
def ajax_autosave_course(request):
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

    if course.status in ('DRAFT', 'WAIT_FOR_APPROVAL', 'READY_TO_PUBLISH'):
        domain_function.persist_course(course, request.POST)
    elif course.status == 'PUBLISHED':
        domain_function.save_course_changes(course, request.POST)

    next_action = request.POST.get('next_action')
    if next_action == 'submit' and course.status == 'DRAFT':
        if domain_function.calculate_course_completeness(course) == 100:
            course.status = 'WAIT_FOR_APPROVAL'
            course.save()
        else:
            return response_json_error_with_message('course-incomplete', errors.COURSE_MODIFICATION_ERRORS)

    elif next_action == 'update' and course.status == 'PUBLISHED':
        if domain_function.calculate_course_completeness(course) == 100:
            domain_function.persist_course_changes(course)
        else:
            return response_json_error_with_message('course-incomplete', errors.COURSE_MODIFICATION_ERRORS)

    return response_json_success({
        'completeness': domain_function.calculate_course_completeness(course),
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

    if course.status in ('DRAFT', 'WAIT_FOR_APPROVAL', 'READY_TO_PUBLISH'):
        editing_course = course
    elif course.status == 'PUBLISHED':
        editing_course = EditingCourse.objects.get(course=course)
        editing_course.is_dirty = True
        editing_course.save()
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
        'completeness': domain_function.calculate_course_completeness(course),
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

    if course.status in ('DRAFT', 'WAIT_FOR_APPROVAL', 'READY_TO_PUBLISH'):
        media_class = CourseOutlineMedia
        picture_media_class = CoursePicture
    elif course.status == 'PUBLISHED':
        media_class = EditingCourseOutlineMedia
        picture_media_class = EditingCoursePicture

        editing_course = EditingCourse.objects.get(course=course)
        editing_course.is_dirty = True
        editing_course.save()
    else:
        return response_json_error_with_message('status-invalid', errors.COURSE_MODIFICATION_ERRORS)

    if media_class.objects.filter(course=course).count() > settings.COURSE_MEDIA_MAXIMUM_NUMBER:
        return response_json_error_with_message('file-number-exceeded', errors.COURSE_MODIFICATION_ERRORS)

    image_file = request.FILES['pictures[]']

    if image_file.size > settings.COURSE_PICTURE_MAXIMUM_SIZE:
        return response_json_error_with_message('file-size-exceeded', errors.COURSE_MODIFICATION_ERRORS)

    course_media = media_class.objects.create(course=course, media_type='PICTURE')

    try:
        course_picture = picture_media_class.objects.create(media=course_media, image=image_file)
        course_picture_url = get_thumbnailer(course_picture.image)['course_picture_small'].url
    except InvalidImageFormatError:
        return response_json_error_with_message('file-type-invalid', errors.COURSE_MODIFICATION_ERRORS)

    response_data = {
        'completeness': domain_function.calculate_course_completeness(course),
        'ordering': media_class.objects.get_media_uid_ordering(course),
        'media_uid': course_media.uid,
        'picture_url': course_picture_url,
    }

    return response_json_success(response_data)


@require_POST
@login_required
def ajax_reorder_course_picture(request):
    if not request.is_ajax():
        raise Http404

    course_uid = request.POST.get('uid')
    course = get_object_or_404(Course, uid=course_uid)

    if course.teacher != request.user:
        return response_json_error_with_message('unauthorized', errors.COURSE_MODIFICATION_ERRORS)

    if course.status in ('DRAFT', 'WAIT_FOR_APPROVAL', 'READY_TO_PUBLISH'):
        media_class = CourseOutlineMedia
    elif course.status == 'PUBLISHED':
        media_class = EditingCourseOutlineMedia

        editing_course = EditingCourse.objects.get(course=course)
        editing_course.is_dirty = True
        editing_course.save()
    else:
        return response_json_error_with_message('status-invalid', errors.COURSE_MODIFICATION_ERRORS)

    ordering = 1
    for media_uid in request.POST.get('ordering').split(','):
        try:
            media = media_class.objects.get(course=course, uid=media_uid)
        except media_class.DoesNotExist:
            pass
        else:
            media.ordering = ordering
            media.save()
            ordering += 1

    return response_json_success({
        'completeness': domain_function.calculate_course_completeness(course),
        'ordering': media_class.objects.get_media_uid_ordering(course),
    })


@require_POST
@login_required
def ajax_delete_course_picture(request):
    if not request.is_ajax():
        raise Http404

    course_uid = request.POST.get('uid')
    course = get_object_or_404(Course, uid=course_uid)

    media_uid = request.POST.get('media_uid')

    if course.teacher != request.user:
        return response_json_error_with_message('unauthorized', errors.COURSE_MODIFICATION_ERRORS)

    if course.status in ('DRAFT', 'WAIT_FOR_APPROVAL', 'READY_TO_PUBLISH'):
        media_class = CourseOutlineMedia
        media = get_object_or_404(CourseOutlineMedia, uid=media_uid)

        if media.media_type == 'PICTURE':
            media_picture = media.coursepicture
            media_picture.image.delete()
            media_picture.delete()
            media.delete()

    elif course.status == 'PUBLISHED':
        media_class = EditingCourseOutlineMedia
        media = get_object_or_404(EditingCourseOutlineMedia, uid=media_uid)

        if media.media_type == 'PICTURE':
            media.mark_deleted = True
            media.save()

        editing_course = EditingCourse.objects.get(course=course)
        editing_course.is_dirty = True
        editing_course.save()
    else:
        return response_json_error_with_message('status-invalid', errors.COURSE_MODIFICATION_ERRORS)

    return response_json_success({
        'completeness': domain_function.calculate_course_completeness(course),
        'ordering': media_class.objects.get_media_uid_ordering(course),
    })


@require_POST
@login_required
def ajax_discard_course_changes(request):
    if not request.is_ajax():
        raise Http404

    course_uid = request.POST.get('uid')
    course = get_object_or_404(Course, uid=course_uid)

    if course.teacher != request.user:
        return response_json_error_with_message('unauthorized', errors.COURSE_MODIFICATION_ERRORS)

    domain_function.discard_course_changes(course)

    return response_json_success({
        'edit_url': reverse('edit_course', args=[course.uid]),
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