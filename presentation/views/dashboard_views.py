# -*- encoding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from django.utils.timezone import now
from common.decorators import teacher_or_student_only, teacher_only

from domain.models import CourseEnrollment, CourseSchedule, Course

# MY COURSES ###########################################################################################################

@login_required
def view_my_courses_upcoming(request):
    rightnow = now()
    upcoming_schedules = CourseSchedule.objects \
        .filter(status='OPENING', start_datetime__gt=rightnow) \
        .filter((Q(course__teacher=request.user) & Q(course__status='PUBLISHED') & Q(status='OPENING'))
                | Q(enrollments__student__in=(request.user,)))

    return render(request, 'dashboard/courses_upcoming.html', {'upcoming_schedules': upcoming_schedules})


@login_required
def view_my_courses_attended(request):
    rightnow = now()
    enrollments = CourseEnrollment.objects\
        .filter(schedule__start_datetime__lte=rightnow, student=request.user, status='CONFIRMED')

    return render(request, 'dashboard/courses_attended.html', {'enrollments': enrollments})


@login_required
def view_my_courses_teaching(request):
    teaching_courses = Course.objects.filter(teacher=request.user)

    return render(request, 'dashboard/courses_teaching.html', {'teaching_courses': teaching_courses})


@login_required
def create_course(request):
    return render(request, 'dashboard/course_create.html', {})


# MANAGE CLASSROOM #####################################################################################################

@login_required
@teacher_only
def manage_classroom_home(request, course, course_uid):
    return render(request, 'dashboard/manage_course_home.html', {'course': course})


@login_required
@teacher_only
def manage_classroom_students(request, course, course_uid):
    return render(request, 'dashboard/manage_course_students.html', {'course': course})


@login_required
@teacher_only
def manage_classroom_calendar(request, course, course_uid):
    return render(request, 'dashboard/manage_course_calendar.html', {'course': course})


@login_required
@teacher_only
def manage_classroom_feedback(request, course, course_uid):
    return render(request, 'dashboard/manage_course_feedback.html', {'course': course})
