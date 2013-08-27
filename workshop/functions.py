from django.conf import settings
from django.utils.timezone import now

from common.errors import WorkshopEnrollmentException
from common.l10n.th import PROVINCE_MAP
from common.utilities import extract_request_object

from workshop.models import WorkshopActivity, WorkshopTopic, Place, WorkshopPicture, Workshop
from reservation.models import Schedule


# WORKSHOP BROWSE ######################################################################################################

def get_popular_workshops():
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


# WORKSHOP DASHBOARD ###################################################################################################

def is_workshop_outline_completed(workshop):
    is_completed = True

    if not workshop.title:
        is_completed = False

    if not WorkshopActivity.objects.filter(workshop=workshop).exists():
        is_completed = False

    if not workshop.description:
        is_completed = False

    if not WorkshopPicture.objects.filter(workshop=workshop).exists():
        is_completed = False

    if not workshop.topics.exists():
        is_completed = False

    if not workshop.default_price:
        is_completed = False

    if not workshop.duration:
        is_completed = False

    if not workshop.default_capacity:
        is_completed = False

    if not workshop.place:
        is_completed = False
    elif workshop.place.is_userdefined and (
            not workshop.place.name or
            not workshop.place.address or
            not workshop.place.province_code or
            not workshop.place.latlng or
            not workshop.place.direction
    ):
        is_completed = False

    return is_completed


def save_workshop(workshop, request_data):
    errors = {}

    if 'title' in request_data:
        workshop.title = request_data['title'].strip(' \t\n\r')

    if 'activity[]' in request_data:
        WorkshopActivity.objects.filter(workshop=workshop).delete()

        bulk = []
        ordering = 1
        for activity in request_data.getlist('activity[]'):
            activity = activity.strip(' \t\n\r')
            if not activity:
                continue

            bulk.append(WorkshopActivity(
                workshop=workshop,
                title=activity,
                ordering=ordering,
            ))
            ordering += 1

        WorkshopActivity.objects.bulk_create(bulk)

    if 'story' in request_data:
        workshop.description = request_data['story'].strip(' \t\n\r')

    if 'picture_ordering' in request_data:
        ordering = 1
        for picture_uid in request_data['picture_ordering'].split(','):
            try:
                picture = WorkshopPicture.objects.get(workshop=workshop, uid=picture_uid)
            except WorkshopPicture.DoesNotExist:
                pass
            else:
                picture.ordering = ordering
                picture.save()
                ordering += 1

    if 'price' in request_data:
        try:
            price = int(request_data['price'])
        except ValueError:
            errors['price'] = 'invalid'
        else:
            if price < settings.WORKSHOP_MINIMUM_PRICE:
                errors['price'] = 'low'
            else:
                workshop.default_price = price

    if 'duration' in request_data:
        try:
            duration = int(request_data['duration'])
            if duration < 1:
                raise ValueError
        except ValueError:
            errors['duration'] = 'invalid'
        else:
            workshop.duration = duration

    if 'capacity' in request_data:
        try:
            capacity = int(request_data['capacity'])
            if capacity < 1:
                raise ValueError
        except ValueError:
            errors['capacity'] = 'invalid'
        else:
            workshop.default_capacity = capacity

    if 'topic' in request_data:
        try:
            topic = WorkshopTopic.objects.get(slug=request_data['topic'])
        except WorkshopTopic.DoesNotExist:
            errors['topic'] = 'not-found'
        else:
            workshop.topics.clear()
            workshop.topics.add(topic)

    if 'place-id' in request_data:
        place_id = request_data.get('place-id')
        if place_id == 'new':
            place = Place.objects.create(is_userdefined=True, is_visible=False, created_by=workshop.teacher)
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

        workshop.place = place
        workshop.save()

        if place and place.created_by == workshop.teacher:
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

    for picture in WorkshopPicture.objects.filter(workshop=workshop, mark_deleted=True):
        picture.image.delete()
        picture.delete()

    for picture in WorkshopPicture.objects.filter(workshop=workshop, mark_added=True):
        picture.mark_added = False
        picture.is_visible = True
        picture.save()

    workshop.save()
    return errors


def revert_approving_workshop(workshop):
    workshop.status = 'DRAFT'
    workshop.save()


# WORKSHOP ENROLLMENT ##################################################################################################

def check_if_schedule_enrollable(schedule):
    if schedule.workshop.status != 'PUBLISHED':
        raise WorkshopEnrollmentException('workshop-notpublished')

    if schedule.status != 'OPENING':
        raise WorkshopEnrollmentException('schedule-notopening')

    if not schedule.stats_seats_left():
        raise WorkshopEnrollmentException('schedule-full')

    return True
