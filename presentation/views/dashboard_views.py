# -*- encoding: utf-8 -*-

import datetime
import operator

from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now
from django.views.decorators.http import require_POST

from common.decorators import teacher_only

from workshop import functions as domain_functions
from workshop.models import Workshop, WorkshopTopic, WorkshopFeedback, WorkshopPicture


# MY WORKSHOPS #########################################################################################################

@login_required
def view_my_courses_payment(request):
    waiting_enrollments = CourseEnrollment.objects.filter(
        student=request.user,
        status='PENDING',
        payment_status='WAIT_FOR_PAYMENT'
    ).order_by('-created')

    return render(request, 'dashboard/courses_payments.html', {'waiting_enrollments': waiting_enrollments})


@login_required
def view_my_courses_upcoming(request):
    rightnow = now()

    upcoming_schedules = []

    for enrollment in CourseEnrollment.objects.filter(
            student=request.user,
            schedule__start_datetime__gt=rightnow,
            status='CONFIRMED'):
        upcoming_schedules.append({
            'schedule': enrollment.schedule,
            'schedule_datetime': enrollment.schedule.start_datetime,
            'type': 'student',
            'enrollment': enrollment,
        })

    for schedule in CourseSchedule.objects.filter(
            status='OPENING',
            start_datetime__gt=rightnow,
            course__teacher=request.user):
        upcoming_schedules.append({
            'schedule': schedule,
            'schedule_datetime': schedule.start_datetime,
            'type': 'teacher',
        })

    upcoming_schedules = sorted(upcoming_schedules, key=operator.itemgetter('schedule_datetime'))

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
    total_enrollments = CourseEnrollment.objects \
        .filter(schedule__start_datetime__lte=rightnow, student=request.user, status='CONFIRMED')

    if not course_school:
        enrollments = total_enrollments
    else:
        enrollments = CourseEnrollment.objects.filter(
            schedule__course__schools__in=(course_school,),
            schedule__start_datetime__lte=rightnow, student=request.user,
            status='CONFIRMED'
        )

    sorted_schools_learned = sorted(
        total_enrollments.values('schedule__course').values('schedule__course__schools__id').annotate(
            num_schools=Count('schedule__course__id')).order_by(),
        key=operator.itemgetter('num_schools'), reverse=True)

    total_num_schools = 0
    schools_learned = []
    for school_learned in sorted_schools_learned:
        schools_learned.append({
            'school': WorkshopTopic.objects.get(id=school_learned['schedule__course__schools__id']),
            'num_schools': school_learned['num_schools'],
        })

        total_num_schools = total_num_schools + school_learned['num_schools']

    return render(request, 'dashboard/courses_attended.html', {
        'enrollments': enrollments,
        'schools_learned': schools_learned,
        'total_num_schools': total_num_schools,
        'course_school': course_school
    })


@login_required
def view_my_courses_teaching(request):
    workshops = Workshop.objects.filter(teacher=request.user).exclude(status='DELETED')

    return render(request, 'dashboard/workshops_organizing.html', {
        'workshops': workshops
    })


# CREATE / EDIT COURSE #################################################################################################

@login_required
def create_course(request):
    course_uid = Workshop.objects.generate_course_uid()
    return render(request, 'dashboard/workshop_modify.html', {
        'course_uid': course_uid,
        'is_completed': False,
    })


@login_required
def edit_workshop(request, workshop_uid):
    workshop = get_object_or_404(Workshop, uid=workshop_uid)

    if workshop.teacher != request.user:
        raise Http404

    workshop_pictures = WorkshopPicture.objects.filter(workshop=workshop, mark_deleted=False)

    return render(request, 'dashboard/workshop_modify.html', {
        'workshop': workshop,
        'workshop_pictures': workshop_pictures,
        'is_completed': domain_functions.is_workshop_outline_completed(workshop),
    })


@require_POST
@login_required
def revert_approving_course(request, course_uid):
    course = get_object_or_404(Workshop, uid=course_uid)

    if course.teacher != request.user:
        raise Http404

    domain_functions.revert_approving_workshop(course)
    return redirect('edit_course', course_uid=course_uid)


# MANAGE CLASSROOM #####################################################################################################

@login_required
@teacher_only
def manage_workshop_overview(request, workshop, workshop_uid):
    rightnow = now()
    upcoming_schedules = CourseSchedule.objects.filter(
        course=course,
        start_datetime__gt=rightnow,
        status='OPENING'
    ).order_by('start_datetime')

    return render(request, 'dashboard/manage_course_overview.html', {
        'course': course,
        'upcoming_schedules': upcoming_schedules
    })


@login_required
@teacher_only
def manage_course_class(request, course, course_uid, datetime_string):
    rightnow = now()

    upcoming_classes = CourseSchedule.objects.filter(course=course, start_datetime__gt=rightnow, status='OPENING').order_by('start_datetime')
    past_classes = CourseSchedule.objects.filter(course=course, start_datetime__lte=rightnow, status='OPENING').order_by('-start_datetime')

    if not datetime_string:
        if upcoming_classes:
            schedule = upcoming_classes[0]
        else:
            schedule = past_classes[0]
    else:
        schedule_datetime = datetime.datetime.strptime(datetime_string, '%Y_%m_%d_%H_%M')
        schedule = get_object_or_404(CourseSchedule, course=course, start_datetime=schedule_datetime)

    if not schedule:
        return render(request, 'dashboard/manage_course_classes.html', {
            'course': course,
            'schedule': schedule,
        })

    if schedule.status != 'OPENING':
        raise Http404

    enrollments = CourseEnrollment.objects.filter(schedule=schedule).order_by('-created')

    return render(request, 'dashboard/manage_course_classes.html', {
        'course': course,
        'schedule': schedule,
        'enrollments': enrollments,
        'upcoming_classes': upcoming_classes,
        'past_classes': past_classes,
    })


@login_required
@teacher_only
def manage_course_feedback(request, course, course_uid, category):
    if not category:
        category = 'all'

    if category == 'all':
        feedbacks = WorkshopFeedback.objects.filter(
            enrollment__schedule__course=course
        ).order_by('-created')
    elif category == 'promoted':
        feedbacks = WorkshopFeedback.objects.filter(
            enrollment__schedule__course=course,
            is_promoted=True
        ).order_by('-created')
    elif category == 'visible':
        feedbacks = WorkshopFeedback.objects.filter(
            enrollment__schedule__course=course,
            is_public=True
        ).order_by('-created')
    elif category == 'invisible':
        feedbacks = WorkshopFeedback.objects.filter(
            enrollment__schedule__course=course,
            is_public=False
        ).order_by('-created')
    else:
        raise Http404

    num_of_feedbacks = {
        'all': WorkshopFeedback.objects.filter(enrollment__schedule__course=course).count(),
        'promoted': WorkshopFeedback.objects.filter(enrollment__schedule__course=course, is_promoted=True).count(),
        'visible': WorkshopFeedback.objects.filter(enrollment__schedule__course=course, is_public=True).count(),
        'invisible': WorkshopFeedback.objects.filter(enrollment__schedule__course=course, is_public=False).count(),
    }

    return render(request, 'dashboard/manage_course_feedback.html', {
        'course': course,
        'feedbacks': feedbacks,
        'num_of_feedbacks': num_of_feedbacks,
        'active_category': category,
    })


@login_required
@teacher_only
def manage_course_promote(request, course, course_uid):
    return render(request, 'dashboard/manage_course_promote.html', {'course': course})


# ENROLLMENT ###########################################################################################################

@login_required
def view_enrollment_details(request, enrollment_code, with_payment):
    enrollment = get_object_or_404(CourseEnrollment, code=enrollment_code, student=request.user)
    return render(request, 'dashboard/enrollment_details.html', {
        'enrollment': enrollment,
        'with_payment': with_payment
    })