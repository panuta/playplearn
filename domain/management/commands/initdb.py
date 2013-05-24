# -*- encoding: utf-8 -*-

import datetime
import pytz

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand

from domain.models import UserAccount, CourseSchool, CourseTopic, Course, CourseSchedule, CourseEnrollment, Venue, CourseVenue


class Command(BaseCommand):
    help = 'Populate initial data to database'

    def handle(self, *args, **options):
        # PRODUCTION CODE ##############################################################################################

        if Site.objects.all().exists():
            Site.objects.all().update(domain=settings.WEBSITE_DOMAIN, name=settings.WEBSITE_NAME)
        else:
            Site.objects.get_or_create(domain=settings.WEBSITE_DOMAIN, name=settings.WEBSITE_NAME)

        some_admin = None
        for admin in settings.ADMINS:
            try:
                user = UserAccount.objects.get(email=admin[1])
            except UserAccount.DoesNotExist:
                user = UserAccount.objects.create_superuser(admin[1], admin[0], '1q2w3e4r')

            some_admin = user

        # DEVELOPMENT CODE #############################################################################################

        if settings.DEBUG:

            # USERS
            try:
                user1 = UserAccount.objects.get(email='user1@example.com')
            except UserAccount.DoesNotExist:
                user1 = UserAccount.objects.create_user('user1@example.com', 'User1 Lastname', '1q2w3e4r')
                user1.headline = 'Wood Carpenter'
                user1.gender = 'M'
                user1.age = 31
                user1.save()

            try:
                user2 = UserAccount.objects.get(email='user2@example.com')
            except UserAccount.DoesNotExist:
                user2 = UserAccount.objects.create_user('user2@example.com', 'User2 Lastname', '1q2w3e4r')
                user2.headline = 'Computer Science Student'
                user2.gender = 'F'
                user2.age = 18
                user2.save()

            try:
                user3 = UserAccount.objects.get(email='user3@example.com')
            except UserAccount.DoesNotExist:
                user3 = UserAccount.objects.create_user('user3@example.com', 'User3 Lastname', '1q2w3e4r')
                user3.headline = 'Avid Learner'
                user3.gender = 'F'
                user3.age = 28
                user3.save()

            # VENUES

            try:
                venue1 = Venue.objects.get(name='House1')
            except Venue.DoesNotExist:
                venue1 = Venue.objects.create(
                    name='House1',
                    address='123 Bangkok',
                    province=10,
                    latlng='100,13',
                )

            # COURSES

            cooking_school, created = CourseSchool.objects.get_or_create(name='School of Cooking')
            engineering_school, created = CourseSchool.objects.get_or_create(name='School of Engineering')
            business_school, created = CourseSchool.objects.get_or_create(name='School of Business')
            craftmanship_school, created = CourseSchool.objects.get_or_create(name='School of Craftmanship')

            watercolor_topic, created = CourseTopic.objects.get_or_create(name='Watercolor Painting')
            programming_topic, created = CourseTopic.objects.get_or_create(name='Programming')
            ux_topic, created = CourseTopic.objects.get_or_create(name='User Experience')
            steak_topic, created = CourseTopic.objects.get_or_create(name='Steak Cooking')
            building_topic, created = CourseTopic.objects.get_or_create(name='Building')

            try:
                course1 = Course.objects.get(uid='COURSE1')
            except Course.DoesNotExist:
                course1 = Course.objects.create(
                    uid='COURSE1',
                    title='How to grill steak',
                    description='I will show you how to grill steak',
                    tuition_fees=500,
                    duration=6,
                    duration_unit='HOURS',
                    minimum_people=10,
                    maximum_people=20,
                    level='ANY',
                    prerequisites='Body',

                    teacher=user1,
                    credentials='I am smart',
                    status='PUBLISHED',
                )

                course1.schools.add(cooking_school)
                course1.topics.add(steak_topic)
                course1.save()

                CourseVenue.objects.create(
                    course=course1,
                    name='Grill House',
                    address='555 Bangkok',
                    province=10,
                    latlng='100,14',
                )

                course1_schedule1 = CourseSchedule.objects.create(
                    course=course1,
                    start_datetime=pytz.timezone('UTC').localize(datetime.datetime(2013, 5, 1, 11, 0), is_dst=None),
                    status='OPENING',
                )

                CourseEnrollment.objects.get_or_create(
                    code='ENROLL1',
                    student=user3,
                    schedule=course1_schedule1,
                    price=500,
                    total=500,
                    payment_status='PAYMENT_RECEIVED',
                    status='CONFIRMED',
                )

            try:
                course2 = Course.objects.get(uid='COURSE2')
            except Course.DoesNotExist:
                course2 = Course.objects.create(
                    uid='COURSE2',
                    title='How to write Django application',
                    description='I will show you how to write Django application',
                    tuition_fees=1000,
                    duration=10,
                    duration_unit='HOURS',
                    minimum_people=2,
                    maximum_people=10,
                    level='BEGINNER',
                    prerequisites='Python',

                    teacher=user2,
                    credentials='I am a programmer',
                    status='PUBLISHED',
                )

                course2.schools.add(engineering_school)
                course2.topics.add(programming_topic)
                course2.save()

                CourseVenue.objects.create(course=course2, venue=venue1)

                course2_schedule1 = CourseSchedule.objects.create(
                    course=course2,
                    start_datetime=pytz.timezone('UTC').localize(datetime.datetime(2013, 5, 30, 10, 0), is_dst=None),
                    status='OPENING',
                )

                CourseEnrollment.objects.get_or_create(
                    code='ENROLL2',
                    student=user3,
                    schedule=course2_schedule1,
                    price=800,
                    total=800,
                    payment_status='PAYMENT_RECEIVED',
                    status='CONFIRMED',
                )

            try:
                course3 = Course.objects.get(uid='COURSE3')
            except Course.DoesNotExist:
                course3 = Course.objects.create(
                    uid='COURSE3',
                    title='How to design a website',
                    description='I will show you how to design a website',
                    tuition_fees=2000,
                    duration=18,
                    duration_unit='HOURS',
                    minimum_people=5,
                    maximum_people=15,
                    level='BEGINNER',
                    prerequisites='Photoshop',

                    teacher=user2,
                    credentials='I am a designer',
                    status='PUBLISHED',
                )

                course3.schools.add(engineering_school)
                course3.topics.add(ux_topic)
                course3.save()

                CourseVenue.objects.create(course=course3, venue=venue1)

                course3_schedule1 = CourseSchedule.objects.create(
                    course=course3,
                    start_datetime=pytz.timezone('UTC').localize(datetime.datetime(2013, 6, 15, 9, 30), is_dst=None),
                    status='OPENING',
                )

                CourseEnrollment.objects.get_or_create(
                    code='ENROLL3',
                    student=user1,
                    schedule=course3_schedule1,
                    price=2000,
                    total=2000,
                    payment_status='PAYMENT_RECEIVED',
                    status='CONFIRMED',
                )

            try:
                course4 = Course.objects.get(uid='COURSE4')
            except Course.DoesNotExist:
                course4 = Course.objects.create(
                    uid='COURSE4',
                    title='How to build a house',
                    description='I will show you how to build a house',
                    tuition_fees=6000,
                    duration=24,
                    duration_unit='HOURS',
                    minimum_people=1,
                    maximum_people=4,
                    level='ADVANCED',
                    prerequisites='Saw',

                    teacher=user1,
                    credentials='I am a carpenter',
                    status='PUBLISHED',
                )

                course4.schools.add(craftmanship_school)
                course4.topics.add(building_topic)
                course4.save()

                CourseVenue.objects.create(
                    course=course4,
                    name='Wood House',
                    address='999 Bangkok',
                    province=10,
                    latlng='100,14',
                )

                course4_schedule1 = CourseSchedule.objects.create(
                    course=course4,
                    start_datetime=pytz.timezone('UTC').localize(datetime.datetime(2013, 6, 30, 8, 0), is_dst=None),
                    status='OPENING',
                )

