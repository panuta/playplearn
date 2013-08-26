# -*- encoding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST

from accounts.forms import EmailAuthenticationForm
from accounts.functions import ajax_login_email_user, ajax_register_email_user

from common import errors
from common.errors import CourseEnrollmentException, ACCOUNT_REGISTRATION_ERRORS, UserRegistrationException
from common.shortcuts import response_json_error, response_json_error_with_message, response_json_success

from domain import functions as domain_functions
from domain.models import Workshop, WorkshopTopic, WorkshopPicture
from reservation.models import Schedule, Reservation


def view_workshop_outline(request, workshop_uid, page_action, reservation_code):
    workshop = get_object_or_404(Workshop, uid=workshop_uid)

    if not workshop.can_view(request.user):
        raise Http404

    rightnow = now()

    pictures = WorkshopPicture.objects.filter(workshop=workshop, is_visible=True).order_by('ordering')

    schedules = Schedule.objects.filter(
        workshop=workshop,
        status='OPENING',
        start_datetime__gte=rightnow
    ).order_by('start_datetime')

    reservation = get_object_or_404(Reservation, code=reservation_code) if reservation_code else None

    return render(request, 'workshop/workshop_outline.html', {
        'workshop': workshop,
        'workshop_pictures': pictures,
        'workshop_schedules': schedules,
        'page_action': page_action,
        'reservation': reservation,
    })


def view_courses_browse(request, browse_by):
    if not browse_by:
        browse_by = 'upcoming'

    if browse_by == 'upcoming':
        courses = domain_functions.get_upcoming_workshops()
        browse_title = _('Upcoming')
    else:
        raise Http404

    return render(request, 'workshop/course_browse.html', {
        'courses': courses,
        'browse_by': browse_by,
        'browse_title': browse_title,
    })


def view_courses_browse_by_topic(request, topic_slug):
    school = get_object_or_404(WorkshopTopic, slug=topic_slug)
    courses = Workshop.objects.filter(status='PUBLISHED', schools__in=(school, ))

    return render(request, 'workshop/course_browse.html', {
        'courses': courses,
        'browse_by': 'topic',
        'browse_title': '%s workshops' % school.name,
        'topic_slug': topic_slug,
    })


def view_course_teach(request):
    return render(request, 'workshop/course_teach.html', {})


def search_course_topics(request):
    pass


@require_POST
def enroll_workshop(request):
    schedule_id = request.POST.get('schedule_id')
    people = request.POST.get('people')

    try:
        schedule = CourseSchedule.objects.get(pk=schedule_id)
    except CourseSchedule.DoesNotExist:
        return response_json_error('schedule-notfound')

    try:
        domain_functions.check_if_schedule_enrollable(schedule)
    except CourseEnrollmentException, e:
        return response_json_error_with_message(e.exception_code, errors.COURSE_ENROLLMENT_ERRORS)

    try:
        people = int(people)
        if people <= 0:
            raise ValueError
    except ValueError:
        return response_json_error_with_message('people-invalid', errors.COURSE_ENROLLMENT_ERRORS)

    if request.user.is_authenticated():
        enrollment = CourseEnrollment.objects.create(
            student=request.user,
            schedule=schedule,
            price=schedule.course.price,
            people=people,
            total=schedule.course.price,
            status='PENDING',
            payment_status='WAIT_FOR_PAYMENT',
        )

        return response_json_success({
            'payment_url': reverse('view_enrollment_details_with_payment', args=[enrollment.code]),
        })

    else:
        # TODO
        return response_json_success({
            'enrollment_code': '',
            'modal_html': render_to_string('snippets/modal_enrollment_login.html', {'schedule': schedule}),
        })


@require_POST
def login_to_enroll_workshop(request, backend):
    if backend not in ('facebook', 'twitter', 'email_login', 'email_signup'):
        raise Http404

    schedule_id = request.POST.get('schedule_id')

    try:
        schedule = CourseSchedule.objects.get(pk=schedule_id)
    except CourseSchedule.DoesNotExist:
        return response_json_error('schedule-notfound')

    try:
        domain_functions.check_if_schedule_enrollable(schedule)
    except CourseEnrollmentException, e:
        return response_json_error_with_message(e.exception_code, errors.COURSE_ENROLLMENT_ERRORS)

    if backend == 'email_login':
        from django.contrib.auth.views import login
        login(request, authentication_form=EmailAuthenticationForm)

        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            ajax_login_email_user(request, email, password)
        except UserRegistrationException, e:
            return response_json_error_with_message(e.exception_code, ACCOUNT_REGISTRATION_ERRORS)

        enrollment = CourseEnrollment.objects.create(
            student=request.user,
            schedule=schedule,
            price=schedule.course.price,
            total=schedule.course.price,
            status='PENDING',
            payment_status='WAIT_FOR_PAYMENT',
        )

        return response_json_success({
            'enrollment_code': enrollment.code,
            'redirect_url': reverse('view_course_outline_with_payment', args=[schedule.course.uid, enrollment.code])
        })

    elif backend == 'email_signup':
        email = request.POST.get('email')

        try:
            registration = ajax_register_email_user(request, email)
        except UserRegistrationException, e:
            return response_json_error_with_message(e.exception_code, ACCOUNT_REGISTRATION_ERRORS)

        unauthenticated_enrollment = UnauthenticatedCourseEnrollment.objects.create(
            key=registration.registration_key,
            schedule=schedule,
            price=schedule.course.price,
            total=schedule.course.price,
        )

        return response_json_success()

    else:
        if backend == 'facebook':
            # TODO
            pass
        elif backend == 'twitter':
            # TODO
            pass
        else:
            raise Http404

        return response_json_success()