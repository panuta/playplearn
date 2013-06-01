# -*- encoding: utf-8 -*-

import operator

from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.shortcuts import render, get_object_or_404
from django.utils.timezone import now
from common.decorators import teacher_only

from domain.models import CourseReservation, CourseSchedule, Course, CourseTopic

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
def view_my_courses_attended_in_topic(request, topic_slug):
    course_topic = get_object_or_404(CourseTopic, slug=topic_slug)
    return _view_my_courses_attended(request, course_topic)


def _view_my_courses_attended(request, course_topic=None):
    rightnow = now()
    total_reservations = CourseReservation.objects \
        .filter(schedule__start_datetime__lte=rightnow, student=request.user, status='CONFIRMED')

    if not course_topic:
        reservations = total_reservations
    else:
        reservations = CourseReservation.objects.filter(schedule__course__topics__in=(course_topic,),
                                                        schedule__start_datetime__lte=rightnow, student=request.user,
                                                        status='CONFIRMED')

    sorted_topics_learned = sorted(
        total_reservations.values('schedule__course').values('schedule__course__topics__id').annotate(
            num_topics=Count('schedule__course__id')).order_by(),
        key=operator.itemgetter('num_topics'), reverse=True)

    total_num_topics = 0
    topics_learned = []
    for topic_learned in sorted_topics_learned:
        topics_learned.append({
            'topic': CourseTopic.objects.get(id=topic_learned['schedule__course__topics__id']),
            'num_topics': topic_learned['num_topics'],
        })

        total_num_topics = total_num_topics + topic_learned['num_topics']

    return render(request, 'dashboard/courses_attended.html',
                  {'reservations': reservations, 'topics_learned': topics_learned, 'total_num_topics': total_num_topics,
                   'course_topic': course_topic})


@login_required
def view_my_courses_teaching(request):
    teaching_courses = Course.objects.filter(teacher=request.user)

    return render(request, 'dashboard/courses_teaching.html', {'teaching_courses': teaching_courses})


@login_required
def create_course(request):
    return render(request, 'dashboard/course_create.html', {})


@login_required
def edit_course(request, course_uid):
    pass


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
