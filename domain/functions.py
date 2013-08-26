from django.conf import settings
from django.utils.timezone import now

from common.errors import CourseEnrollmentException
from common.l10n.th import PROVINCE_MAP
from common.utilities import extract_request_object

from domain.models import WorkshopActivity, WorkshopTopic, Place, WorkshopPicture, Workshop
from reservation.models import Schedule


# COURSE BROWSE ########################################################################################################

def get_popular_courses():
    pass


def get_upcoming_workshops():
    rightnow = now()

    upcoming_schedules = Schedule.objects.filter(
        workshop__status=Workshop.STATUS_PUBLISHED,
        status=Schedule.STATUS_OPEN,
        start_datetime__gt=rightnow
    ).order_by('start_datetime')

    upcoming_workshops = []
    for schedule in upcoming_schedules:
        if schedule.workshop not in upcoming_workshops:
            upcoming_workshops.append(schedule.workshop)

        if len(upcoming_workshops) > settings.DISPLAY_HOMEPAGE_WORKSHOPS:
            break

    return upcoming_workshops


# COURSE DASHBOARD #####################################################################################################

def is_course_outline_completed(course):
    is_completed = True

    if not course.title:
        is_completed = False

    if not WorkshopActivity.objects.filter(course=course).exists():
        is_completed = False

    if not course.description:
        is_completed = False

    if not course.cover:
        is_completed = False

    if not WorkshopPicture.objects.filter(course=course).exists():
        is_completed = False

    if not course.schools.exists():
        is_completed = False

    if not course.price:
        is_completed = False

    if not course.duration:
        is_completed = False

    if not course.maximum_people:
        is_completed = False

    if not course.place:
        is_completed = False
    elif course.place.is_userdefined and (
            not course.place.name or
            not course.place.address or
            not course.place.province_code or
            not course.place.latlng or
            not course.place.direction
    ):
        is_completed = False

    return is_completed


def save_course(course, request_data):
    errors = {}

    if 'title' in request_data:
        course.title = request_data['title'].strip(' \t\n\r')

    if 'activity[]' in request_data:
        WorkshopActivity.objects.filter(course=course).delete()

        bulk = []
        ordering = 1
        for activity in request_data.getlist('activity[]'):
            activity = activity.strip(' \t\n\r')
            if not activity:
                continue

            bulk.append(WorkshopActivity(
                course=course,
                title=activity,
                ordering=ordering,
            ))
            ordering += 1

        WorkshopActivity.objects.bulk_create(bulk)

    if 'story' in request_data:
        course.description = request_data['story'].strip(' \t\n\r')

    picture_descriptions = extract_request_object(request_data, 'picture_descriptions')
    if picture_descriptions:
        for picture_key in picture_descriptions.keys():
            media_uid = picture_descriptions[picture_key]['uid']

            try:
                picture = WorkshopPicture.objects.get(course=course, uid=media_uid)
            except WorkshopPicture.DoesNotExist:
                pass
            else:
                picture.description = picture_descriptions[picture_key]['description']
                picture.save()

    if 'picture_ordering' in request_data:
        ordering = 1
        for picture_uid in request_data['picture_ordering'].split(','):
            try:
                picture = WorkshopPicture.objects.get(course=course, uid=picture_uid)
            except WorkshopPicture.DoesNotExist:
                pass
            else:
                picture.ordering = ordering
                picture.save()
                ordering += 1

    if 'school' in request_data:
        try:
            school = WorkshopTopic.objects.get(slug=request_data['school'])
        except WorkshopTopic.DoesNotExist:
            errors['school'] = 'not-found'
        else:
            course.schools.clear()
            course.schools.add(school)

    if 'price' in request_data:
        try:
            price = int(request_data['price'])
        except ValueError:
            errors['price'] = 'invalid'
        else:
            if price < settings.COURSE_PRICE_MINIMUM:
                errors['price'] = 'low'
            else:
                course.price = price

    if 'duration' in request_data:
        try:
            duration = int(request_data['duration'])
            if duration < 1:
                raise ValueError
        except ValueError:
            errors['duration'] = 'invalid'
        else:
            course.duration = duration

    if 'capacity' in request_data:
        try:
            capacity = int(request_data['capacity'])
            if capacity < 1:
                raise ValueError
        except ValueError:
            errors['capacity'] = 'invalid'
        else:
            course.maximum_people = capacity

    if 'place-id' in request_data:
        place_id = request_data.get('place-id')
        if place_id == 'new':
            place = Place.objects.create(is_userdefined=True, is_visible=False, created_by=course.teacher)
        elif place_id:
            try:
                place = Place.objects.get(pk=request_data.get('place-id'))
            except ValueError:
                errors['place-id'] = 'invalid'
                place = None
            except Place.DoesNotExist:
                errors['place-id'] = 'invalid'
                place = None
        else:
            place = None

        course.place = place
        course.save()

        if place and place.created_by == course.teacher:
            if 'place-name' in request_data:
                place.name = request_data['place-name'].strip(' \t\n\r')

            if 'place-address' in request_data:
                place.address = request_data['place-address'].strip(' \t\n\r')

            if 'place-province' in request_data:
                province_code = request_data['place-province']

                if province_code in PROVINCE_MAP:
                    place.province_code = province_code
                else:
                    errors['place-province'] = 'invalid'

            if 'place-location' in request_data:
                place.latlng = request_data['place-location']

            if 'place-direction' in request_data:
                place.direction = request_data['place-direction'].strip(' \t\n\r')

            place.save()

    # Save editing pictures

    for picture in WorkshopPicture.objects.filter(course=course, mark_deleted=True):
        picture.image.delete()
        picture.delete()

    for picture in WorkshopPicture.objects.filter(course=course, mark_added=True):
        picture.mark_added = False
        picture.is_visible = True
        picture.save()

    course.save()
    return errors


def revert_approving_workshop(workshop):
    workshop.status = 'DRAFT'
    workshop.save()


# COURSE ENROLLMENT ####################################################################################################

def check_if_schedule_enrollable(schedule):
    if schedule.course.status != 'PUBLISHED':
        raise CourseEnrollmentException('course-notpublished')

    if schedule.status != 'OPENING':
        raise CourseEnrollmentException('schedule-notopening')

    if not schedule.stats_seats_left():
        raise CourseEnrollmentException('schedule-full')

    return True
