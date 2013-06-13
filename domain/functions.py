from django.conf import settings
from django.core.files.base import ContentFile

from common.constants.course import COURSE_LEVEL_MAP
from common.l10n.th import PROVINCE_MAP
from common.utilities import extract_request_object
from domain.models import EditingCourseOutline, CourseOutline, CourseSchool, CourseOutlineMedia, EditingCourse, EditingCourseOutlineMedia, EditingCoursePicture, EditingCourseVideoURL, course_cover_dir, CoursePicture, CourseVideoURL, Place, EditingPlace


def calculate_course_completeness(course):
    has_changes = course.status == 'PUBLISHED' and EditingCourseOutline.objects.filter(course=course).exists()

    percentage = 0

    if not has_changes:
        percentage += 10 if course.title else 0
        percentage += 10 if CourseOutline.objects.filter(course=course).exists() else 0
        percentage += 20 if course.description else 0

        percentage += 10 if course.cover else 0
        percentage += 10 if CourseOutlineMedia.objects.filter(course=course).exclude(description='').exists() else 0

        percentage += 5 if course.schools.exists() else 0
        percentage += 5 if course.tags.exists() else 0
        percentage += 5 if course.level else 0
        percentage += 5 if course.price else 0
        percentage += 5 if course.duration else 0
        percentage += 5 if course.maximum_people else 0

        percentage += 10 if course.place else 0

    else:
        editing_course = course.editingcourse

        percentage += 10 if editing_course.title else 0
        percentage += 10 if EditingCourseOutline.objects.filter(course=course).exists() else 0
        percentage += 20 if editing_course.description else 0

        percentage += 10 if editing_course.cover else 0
        percentage += 10 if EditingCourseOutlineMedia.objects.filter(course=course).exclude(description='').exists() else 0

        percentage += 5 if editing_course.schools.exists() else 0
        percentage += 5 if editing_course.tags.exists() else 0
        percentage += 5 if editing_course.level else 0
        percentage += 5 if editing_course.price else 0
        percentage += 5 if editing_course.duration else 0
        percentage += 5 if editing_course.maximum_people else 0

        percentage += 10 if editing_course.place else 0

    return percentage


def persist_course(course, request_data):
    errors = {}

    if 'title' in request_data:
        course.title = request_data['title'].strip(' \t\n\r')

    if 'outline[]' in request_data:
        CourseOutline.objects.filter(course=course).delete()

        bulk = []
        ordering = 1
        for outline in request_data.getlist('outline[]'):
            outline = outline.strip(' \t\n\r')
            if not outline:
                continue

            bulk.append(CourseOutline(
                course=course,
                title=outline,
                ordering=ordering,
            ))
            ordering += 1

        CourseOutline.objects.bulk_create(bulk)

    if 'story' in request_data:
        course.description = request_data['story'].strip(' \t\n\r')

    media_desc = extract_request_object(request_data, 'media_desc')
    if media_desc:
        for media_key in media_desc.keys():
            media_uid = media_desc[media_key]['uid']

            try:
                media = CourseOutlineMedia.objects.get(course=course, uid=media_uid)
            except CourseOutlineMedia.DoesNotExist:
                pass
            else:
                media.description = media_desc[media_key]['description']
                media.save()

    if 'media_ordering' in request_data:
        ordering = 1
        for media_uid in request_data['media_ordering'].split(','):
            try:
                media = CourseOutlineMedia.objects.get(course=course, uid=media_uid)
            except CourseOutlineMedia.DoesNotExist:
                pass
            else:
                media.ordering = ordering
                media.save()
                ordering += 1

    if 'school' in request_data:
        try:
            school = CourseSchool.objects.get(slug=request_data['school'])
        except CourseSchool.DoesNotExist:
            errors['school'] = 'not-found'
        else:
            course.schools.clear()
            course.schools.add(school)

    if 'topics' in request_data:
        cleaned_topics = []
        for topic in request_data['topics'].split(','):
            topic = topic.strip(' \t\n\r')

            if topic and topic not in cleaned_topics:
                cleaned_topics.append(topic)

        course.tags.clear()
        course.tags.add(*cleaned_topics)

    if 'level' in request_data:
        if request_data['level'] in COURSE_LEVEL_MAP:
            course.level = request_data['level']
        else:
            errors['level'] = 'invalid'

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

    if 'place' in request_data:
        place_choice = request_data['place']

        if place_choice == 'defined-place':
            try:
                place = Place.objects.get(pk=request_data.get('place-defined'))  # TODO
            except ValueError:
                errors['place-defined'] = 'invalid'
            except Place.DoesNotExist:
                errors['place-defined'] = 'invalid'
            else:
                if course.place and course.place.is_userdefined:
                    course.place.delete()
                course.place = place

        elif place_choice == 'userdefined-place':
            if not course.place or (course.place and not course.place.is_userdefined):
                course.place = Place.objects.create(is_userdefined=True, is_visible=False)

            if 'place-name' in request_data:
                course.place.name = request_data['place-name'].strip(' \t\n\r')

            if 'place-phone' in request_data:
                course.place.phone_number = request_data['place-phone'].strip(' \t\n\r')

            if 'place-address' in request_data:
                course.place.address = request_data['place-address'].strip(' \t\n\r')

            if 'place-province' in request_data:
                province_code = request_data['place-province']

                if province_code in PROVINCE_MAP:
                    course.place.province_code = province_code
                else:
                    errors['place-province'] = 'invalid'

            if 'place-location' in request_data:
                course.place.latlng = request_data['place-location']

            if 'place-direction' in request_data:
                course.place.direction = request_data['place-direction'].strip(' \t\n\r')

            course.place.save()

        else:
            errors['place'] = 'invalid'

    course.save()
    return errors


def has_course_changes(course):
    has_changes = False
    if course.status == 'PUBLISHED':
        if EditingCourse.objects.filter(course=course).exists():
            has_changes = True

        if EditingCourseOutline.objects.filter(course=course).exists():
            has_changes = True

        if EditingCourseOutlineMedia.objects.filter(course=course).exists():
            has_changes = True

        if EditingPlace.objects.filter(course=course).exists():
            has_changes = True

    return has_changes


def save_course_changes(course, request_data):
    errors = {}
    editing_course = EditingCourse.objects.get(course=course)

    if 'title' in request_data:
        editing_course.title = request_data['title'].strip(' \t\n\r')

    if 'outline[]' in request_data:
        EditingCourseOutline.objects.filter(course=course).delete()

        bulk = []
        ordering = 1
        for outline in request_data.getlist('outline[]'):
            outline = outline.strip(' \t\n\r')
            if not outline:
                continue

            bulk.append(EditingCourseOutline(
                course=course,
                title=outline,
                ordering=ordering,
            ))
            ordering += 1

        EditingCourseOutline.objects.bulk_create(bulk)

    if 'story' in request_data:
        editing_course.description = request_data['story'].strip(' \t\n\r')

    media_desc = extract_request_object(request_data, 'media_desc')
    if media_desc:
        for media_key in media_desc.keys():
            media_uid = media_desc[media_key]['uid']

            try:
                media = EditingCourseOutlineMedia.objects.get(course=course, uid=media_uid)
            except EditingCourseOutlineMedia.DoesNotExist:
                pass
            else:
                media.description = media_desc[media_key]['description']
                media.save()

    if 'media_ordering' in request_data:
        ordering = 1
        for media_uid in request_data['media_ordering'].split(','):
            try:
                media = EditingCourseOutlineMedia.objects.get(course=course, uid=media_uid)
            except EditingCourseOutlineMedia.DoesNotExist:
                pass
            else:
                media.ordering = ordering
                media.save()
                ordering += 1

    if 'school' in request_data:
        try:
            school = CourseSchool.objects.get(slug=request_data['school'])
        except CourseSchool.DoesNotExist:
            errors['school'] = 'not-found'
        else:
            editing_course.schools.clear()
            editing_course.schools.add(school)

    if 'topics' in request_data:
        cleaned_topics = []
        for topic in request_data['topics'].split(','):
            topic = topic.strip(' \t\n\r')

            if topic and topic not in cleaned_topics:
                cleaned_topics.append(topic)

        editing_course.tags.clear()
        editing_course.tags.add(*cleaned_topics)

    if 'level' in request_data:
        if request_data['level'] in COURSE_LEVEL_MAP:
            editing_course.level = request_data['level']
        else:
            errors['level'] = 'invalid'

    if 'price' in request_data:
        try:
            price = int(request_data['price'])
        except ValueError:
            errors['price'] = 'invalid'
        else:
            if price < settings.COURSE_PRICE_MINIMUM:
                errors['price'] = 'low'
            else:
                editing_course.price = price

    if 'duration' in request_data:
        try:
            duration = int(request_data['duration'])
            if duration < 1:
                raise ValueError
        except ValueError:
            errors['duration'] = 'invalid'
        else:
            editing_course.duration = duration

    if 'capacity' in request_data:
        try:
            capacity = int(request_data['capacity'])
            if capacity < 1:
                raise ValueError
        except ValueError:
            errors['capacity'] = 'invalid'
        else:
            editing_course.maximum_people = capacity

    if 'place' in request_data:
        place_choice = request_data['place']

        editing_place, _ = EditingPlace.objects.get_or_create(course=course)

        if place_choice == 'defined-place':
            try:
                place = Place.objects.get(pk=request_data.get('place-defined'))
            except ValueError:
                errors['place-defined'] = 'invalid'
            except Place.DoesNotExist:
                errors['place-defined'] = 'invalid'
            else:
                editing_place.is_userdefined = False
                editing_place.defined_place = place
                editing_place.name = ''
                editing_place.phone_number = ''
                editing_place.address = ''
                editing_place.province_code = ''
                editing_place.latlng = ''
                editing_place.direction = ''

        elif place_choice == 'userdefined-place':
            if 'place-name' in request_data:
                editing_place.name = request_data['place-name'].strip(' \t\n\r')

            if 'place-phone' in request_data:
                editing_place.phone_number = request_data['place-phone'].strip(' \t\n\r')

            if 'place-address' in request_data:
                editing_place.address = request_data['place-address'].strip(' \t\n\r')

            if 'place-province' in request_data:
                province_code = request_data['place-province']

                if province_code in PROVINCE_MAP:
                    editing_place.province_code = province_code
                else:
                    errors['place-province'] = 'invalid'

            if 'place-location' in request_data:
                editing_place.latlng = request_data['place-location']

            if 'place-direction' in request_data:
                editing_place.direction = request_data['place-direction'].strip(' \t\n\r')

            editing_place.is_userdefined = True

        else:
            errors['place'] = 'invalid'

        editing_place.save()

    editing_course.is_dirty = True
    editing_course.save()
    return errors


def persist_course_changes(course):
    try:
        editing_course = EditingCourse.objects.get(course=course)
    except EditingCourse.DoesNotExist:
        pass
    else:
        course.title = editing_course.title
        course.description = editing_course.description

        if editing_course.cover:
            cover = ContentFile(editing_course.cover.read())
            cover.name = course_cover_dir(course, editing_course.cover.name)
        else:
            cover = None

        # TODO Test if there is cover already
        course.cover = cover

        course.schools.clear()
        course.schools.add(*editing_course.schools.all())

        course.tags.clear()
        course.tags.add(*editing_course.tags.all())

        course.price = editing_course.price
        course.price_unit = editing_course.price_unit
        course.duration = editing_course.duration
        course.maximum_people = editing_course.maximum_people
        course.level = editing_course.level
        course.prerequisites = editing_course.prerequisites
        course.credentials = editing_course.credentials

        course.save()
        editing_course.delete()

    if EditingCourseOutline.objects.filter(course=course).exists():
        bulk = []
        for editing_outline in EditingCourseOutline.objects.filter(course=course):
            bulk.append(CourseOutline(
                course=course,
                title=editing_outline.title,
                description=editing_outline.description,
                ordering=editing_outline.ordering,
            ))

        EditingCourseOutline.objects.bulk_create(bulk)
        CourseOutline.objects.filter(course=course).delete()

    if EditingCourseOutlineMedia.objects.filter(course=course).exists():
        for editing_media in EditingCourseOutlineMedia.objects.filter(course=course):
            if editing_media.is_new and not editing_media.mark_deleted:
                # New media file
                media = CourseOutlineMedia.objects.create(
                    uid=editing_media.uid,
                    course=course,
                    media_type=editing_media.media_type,
                    description=editing_media.description,
                    ordering=editing_media.ordering,
                    uploaded=editing_media.uploaded,
                )

                if editing_media.media_type == 'PICTURE':
                    CoursePicture.objects.create(
                        media=media,
                        image=editing_media.editingcoursepicture.image,
                    )

                elif editing_media.media_type == 'VIDEO_URL':
                    CourseVideoURL.objects.create(
                        media=media,
                        url=editing_media.coursevideourl.url,
                    )

            elif not editing_media.is_new and editing_media.marked_deleted:
                # Remove old file

                try:
                    media = CourseOutlineMedia.objects.get(uid=editing_media.uid)
                except CourseOutlineMedia.DoesNotExist:
                    pass
                else:
                    if editing_media.media_type == 'PICTURE':
                        media.coursepicture.image.delete()
                        media.coursepicture.delete()

                    elif editing_media.media_type == 'VIDEO_URL':
                        media.coursevideourl.delete()

                    media.delete()

        EditingCoursePicture.objects.filter(editing_media__course=course).delete()
        EditingCourseVideoURL.objects.filter(editing_media__course=course).delete()
        EditingCourseOutlineMedia.objects.filter(course=course).delete()

    try:
        editing_place = EditingPlace.objects.get(course=course)
    except EditingPlace.DoesNotExist:
        pass
    else:
        if editing_place.is_userdefined:
            if not course.place.is_userdefined:
                course.place = Place.objects.create(
                    is_userdefined=True,
                    name=editing_place.name,
                    phone_number=editing_place.phone_number,
                    address=editing_place.address,
                    province_code=editing_place.province_code,
                    latlng=editing_place.latlng,
                    direction=editing_place.direction,
                )
                course.save()
            else:
                course.place.name = editing_place.name
                course.place.phone_number = editing_place.phone_number
                course.place.address = editing_place.address
                course.place.province_code = editing_place.province_code
                course.place.latlng = editing_place.latlng
                course.place.direction = editing_place.direction

                course.place.save()
        else:
            if course.place.is_userdefined:
                course.place.delete()

            course.place = editing_place.defined_place
            course.save()


def discard_course_changes(course):
    EditingCourse.objects.filter(course=course).delete()
    EditingCourseOutline.objects.filter(course=course).delete()

    for editing_media in EditingCourseOutlineMedia.objects.filter(course=course):
        if editing_media.media_type == 'PICTURE':
            editing_media_picture = EditingCoursePicture.objects.get(editing_media=editing_media)

            if editing_media.is_new:
                editing_media_picture.image.delete()

            editing_media_picture.delete()
        elif editing_media.media_type == 'VIDEO_URL':
            editing_media_video = EditingCourseVideoURL.objects.get(editing_media=editing_media)
            editing_media_video.delete()

        editing_media.delete()
