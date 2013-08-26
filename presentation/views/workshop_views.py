# -*- encoding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST

from account.forms import EmailAuthenticationForm
from account.functions import ajax_login_email_user, ajax_register_email_user

from common import errors
from common.errors import WorkshopEnrollmentException, ACCOUNT_REGISTRATION_ERRORS, UserRegistrationException
from common.shortcuts import response_json_error, response_json_error_with_message, response_json_success

from workshop import functions as domain_functions
from workshop.models import Workshop, WorkshopTopic, WorkshopPicture
from reservation.models import Schedule, Reservation


def view_workshop_outline(request, workshop_uid, page_action, reservation_code):
    workshop = get_object_or_404(Workshop, uid=workshop_uid)

    if not workshop.can_view(request.user):
        raise Http404

    rightnow = now()

    pictures = WorkshopPicture.objects.filter(workshop=workshop, is_visible=True).order_by('ordering')

    upcoming_schedule = workshop.get_available_upcoming_schedule()
    schedules = Schedule.objects.filter(
        workshop=workshop,
        status=Schedule.STATUS_OPEN,
        start_datetime__gte=rightnow
    ).order_by('start_datetime')

    reservation = get_object_or_404(Reservation, code=reservation_code) if reservation_code else None

    return render(request, 'workshop/workshop_outline.html', {
        'workshop': workshop,
        'workshop_pictures': pictures,
        'upcoming_schedule': upcoming_schedule,
        'workshop_schedules': schedules,
        'page_action': page_action,
        'reservation': reservation,
    })


def view_workshops_browse(request, browse_by):
    if not browse_by:
        browse_by = 'upcoming'

    if browse_by == 'upcoming':
        workshops = domain_functions.get_upcoming_workshops()
        browse_title = _('Upcoming')
    else:
        raise Http404

    return render(request, 'workshop/workshop_browse.html', {
        'workshops': workshops,
        'browse_by': browse_by,
        'browse_title': browse_title,
    })


def view_workshops_browse_by_topic(request, topic_slug):
    school = get_object_or_404(WorkshopTopic, slug=topic_slug)
    workshops = Workshop.objects.filter(status='PUBLISHED', schools__in=(school, ))

    return render(request, 'workshop/workshop_browse.html', {
        'workshops': workshops,
        'browse_by': 'topic',
        'browse_title': '%s workshops' % school.name,
        'topic_slug': topic_slug,
    })


def view_workshop_teach(request):
    return render(request, 'workshop/workshop_teach.html', {})


def search_workshop_topics(request):
    pass


@require_POST
def enroll_workshop(request):
    schedule_id = request.POST.get('schedule_id')
    people = request.POST.get('people')

    try:
        schedule = WorkshopSchedule.objects.get(pk=schedule_id)
    except WorkshopSchedule.DoesNotExist:
        return response_json_error('schedule-notfound')

    try:
        domain_functions.check_if_schedule_enrollable(schedule)
    except WorkshopEnrollmentException, e:
        return response_json_error_with_message(e.exception_code, errors.WORKSHOP_ENROLLMENT_ERRORS)

    try:
        people = int(people)
        if people <= 0:
            raise ValueError
    except ValueError:
        return response_json_error_with_message('people-invalid', errors.WORKSHOP_ENROLLMENT_ERRORS)

    if request.user.is_authenticated():
        enrollment = WorkshopEnrollment.objects.create(
            student=request.user,
            schedule=schedule,
            price=schedule.workshop.price,
            people=people,
            total=schedule.workshop.price,
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
        schedule = WorkshopSchedule.objects.get(pk=schedule_id)
    except WorkshopSchedule.DoesNotExist:
        return response_json_error('schedule-notfound')

    try:
        domain_functions.check_if_schedule_enrollable(schedule)
    except WorkshopEnrollmentException, e:
        return response_json_error_with_message(e.exception_code, errors.WORKSHOP_ENROLLMENT_ERRORS)

    if backend == 'email_login':
        from django.contrib.auth.views import login
        login(request, authentication_form=EmailAuthenticationForm)

        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            ajax_login_email_user(request, email, password)
        except UserRegistrationException, e:
            return response_json_error_with_message(e.exception_code, ACCOUNT_REGISTRATION_ERRORS)

        enrollment = WorkshopEnrollment.objects.create(
            student=request.user,
            schedule=schedule,
            price=schedule.workshop.price,
            total=schedule.workshop.price,
            status='PENDING',
            payment_status='WAIT_FOR_PAYMENT',
        )

        return response_json_success({
            'enrollment_code': enrollment.code,
            'redirect_url': reverse('view_workshop_outline_with_payment', args=[schedule.workshop.uid, enrollment.code])
        })

    elif backend == 'email_signup':
        email = request.POST.get('email')

        try:
            registration = ajax_register_email_user(request, email)
        except UserRegistrationException, e:
            return response_json_error_with_message(e.exception_code, ACCOUNT_REGISTRATION_ERRORS)

        unauthenticated_enrollment = UnauthenticatedWorkshopEnrollment.objects.create(
            key=registration.registration_key,
            schedule=schedule,
            price=schedule.workshop.price,
            total=schedule.workshop.price,
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