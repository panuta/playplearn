# -*- encoding: utf-8 -*-

import datetime
import operator

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Q, Count
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.utils.timezone import now
from django.views.decorators.http import require_GET, require_POST

from easy_thumbnails.exceptions import InvalidImageFormatError
from easy_thumbnails.files import get_thumbnailer

from common import errors
from common.constants.course import COURSE_RESERVATION_STATUS_MAP, COURSE_RESERVATION_PAYMENT_STATUS_MAP
from common.constants.currency import CURRENCY_CODE_MAP
from common.decorators import teacher_only
from common.shortcuts import response_json_success, response_json_error, response_json_error_with_message
from common.utilities import format_full_datetime

from domain import functions as domain_function
from domain.models import CourseReservation, CourseSchedule, Course, CourseSchool, CourseOutlineMedia, CoursePicture, EditingCourse, EditingCourseOutlineMedia, EditingCoursePicture

# MY COURSES ###########################################################################################################

@login_required
def view_my_courses_upcoming(request):
    rightnow = now()
    upcoming_schedules = CourseSchedule.objects \
        .filter(status='OPENING', start_datetime__gt=rightnow) \
        .filter((Q(course__teacher=request.user) & Q(course__status='PUBLISHED') & Q(status='OPENING'))
                | Q(reservations__student__in=(request.user,)))

    return render(request, 'dashboard/courses_upcoming.html', {'upcoming_schedules': upcoming_schedules})


@login_required
def view_my_courses_attended(request):
    return _view_my_courses_attended(request)


@login_required
def view_my_courses_attended_in_school(request, school_slug):
    course_school = get_object_or_404(CourseSchedule, slug=school_slug)
    return _view_my_courses_attended(request, course_school)


def _view_my_courses_attended(request, course_school=None):
    rightnow = now()
    total_reservations = CourseReservation.objects \
        .filter(schedule__start_datetime__lte=rightnow, student=request.user, status='CONFIRMED')

    if not course_school:
        reservations = total_reservations
    else:
        reservations = CourseReservation.objects.filter(schedule__course__schools__in=(course_school,),
                                                        schedule__start_datetime__lte=rightnow, student=request.user,
                                                        status='CONFIRMED')

    sorted_schools_learned = sorted(
        total_reservations.values('schedule__course').values('schedule__course__schools__id').annotate(
            num_schools=Count('schedule__course__id')).order_by(),
        key=operator.itemgetter('num_schools'), reverse=True)

    total_num_schools = 0
    schools_learned = []
    for school_learned in sorted_schools_learned:
        schools_learned.append({
            'school': CourseSchool.objects.get(id=school_learned['schedule__course__schools__id']),
            'num_schools': school_learned['num_schools'],
        })

        total_num_schools = total_num_schools + school_learned['num_schools']

    return render(request, 'dashboard/courses_attended.html', {
        'reservations': reservations,
        'schools_learned': schools_learned,
        'total_num_schools': total_num_schools,
        'course_school': course_school
    })


@login_required
def view_my_courses_teaching(request):
    teaching_courses = Course.objects.filter(teacher=request.user)

    return render(request, 'dashboard/courses_teaching.html', {'teaching_courses': teaching_courses})


@login_required
def create_course(request):
    course_uid = Course.objects.generate_course_uid()
    editing_course = Course()
    return render(request, 'dashboard/course_modify.html', {
        'course_uid': course_uid,
        'editing_course': editing_course,
        'editing_place': editing_course.get_editing_place(),
    })


@login_required
def edit_course(request, course_uid):
    course = get_object_or_404(Course, uid=course_uid)

    if course.teacher != request.user:
        raise Http404

    if course.status in ('DRAFT', 'WAIT_FOR_APPROVAL', 'READY_TO_PUBLISH'):
        editing_course = course
    elif course.status == 'PUBLISHED':
        try:
            editing_course = EditingCourse.objects.get(course=course)
        except EditingCourse.DoesNotExist:
            editing_course = course.create_editing_course()
    else:
        raise Http404

    has_changes = domain_function.has_course_changes(course)
    return render(request, 'dashboard/course_modify.html', {
        'course': course,
        'editing_course': editing_course,
        'editing_place': editing_course.get_editing_place(),
        'completeness': course.completeness(),
        'has_changes': has_changes,
    })


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

    course.status = 'PUBLISHED'
    course.last_scheduled = now()
    course.save()

    CourseOutlineMedia.objects.filter(course=course).update(is_visible=True)

    if course.place.is_userdefined:
        course.place.is_visible = True
        course.place.save()

    messages.success(request, 'Successfully publish your course. You can now promote the course here.')

    return response_json_success({
        'redirect_url': reverse('manage_course_promote', args=[course.uid]),
    })


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
        datetime_data = '%s-%s' % (request.POST.get('schedule_date'), request.POST.get('schedule_time'))
        schedule_datetime = datetime.datetime.strptime(datetime_data, '%Y-%m-%d-%H-%M')
    except ValueError:
        return response_json_error_with_message('input-invalid', errors.COURSE_MODIFICATION_ERRORS)

    CourseSchedule.objects.create(course=course, start_datetime=schedule_datetime)

    course.last_scheduled = now()
    course.save()

    return response_json_success()


@require_GET
@login_required
def ajax_view_reservation_details(request):
    if not request.is_ajax():
        raise Http404

    code = request.GET.get('code')

    try:
        reservation = CourseReservation.objects.get(code=code)
    except CourseReservation.DoesNotExist:
        raise Http404

    course = reservation.schedule.course
    return response_json_success({
        'title': course.title,
        'teacher_name': course.teacher.name,
        'schedule_datetime': format_full_datetime(reservation.schedule.start_datetime),
        'amount': '%.0f %s' % (reservation.total, CURRENCY_CODE_MAP[str(course.price_unit)]['name']),
        'status': COURSE_RESERVATION_STATUS_MAP[str(reservation.status)]['name'],
        'payment_status': COURSE_RESERVATION_PAYMENT_STATUS_MAP[str(reservation.payment_status)]['name'],
        'reserved_on': format_full_datetime(reservation.created),
        'print_url': '',
    })


def print_reservation(request, reservation_code):
    reservation = get_object_or_404(CourseReservation, code=reservation_code)
    return render(request, 'dashboard/reservation_print.html', {'reservation': reservation})


# MANAGE CLASSROOM #####################################################################################################

@login_required
@teacher_only
def manage_course_overview(request, course, course_uid):
    return render(request, 'dashboard/manage_course_overview.html', {'course': course})


@login_required
@teacher_only
def manage_course_students(request, course, course_uid):
    return render(request, 'dashboard/manage_course_students.html', {'course': course})


@login_required
@teacher_only
def manage_course_feedback(request, course, course_uid):
    return render(request, 'dashboard/manage_course_feedback.html', {'course': course})


@login_required
@teacher_only
def manage_course_promote(request, course, course_uid):
    return render(request, 'dashboard/manage_course_promote.html', {'course': course})