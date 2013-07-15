# -*- encoding: utf-8 -*-

import datetime
from decimal import Decimal
import pytz

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand

from domain.models import UserAccount, CourseSchool, Course, CourseSchedule, CourseEnrollment, Place, UserAccountBalanceTransaction, CourseFeedback


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
                user.headline = 'Superuser'
                user.phone_number = '999-999-9999'
                user.save()

            some_admin = user

        craftmanship_school, created = CourseSchool.objects.get_or_create(name='Craftmanship', slug='craftmanship')
        culinary_arts_school, created = CourseSchool.objects.get_or_create(name='Culinary Arts', slug='culinary_arts')
        design_school, created = CourseSchool.objects.get_or_create(name='Design', slug='design')
        entrepreneurship_school, created = CourseSchool.objects.get_or_create(name='Entrepreneurship', slug='entrepreneurship')
        fashion_and_style_school, created = CourseSchool.objects.get_or_create(name='Fashion & Style', slug='fashion_and_style')
        photography_school, created = CourseSchool.objects.get_or_create(name='Photography', slug='photography')
        technology_school, created = CourseSchool.objects.get_or_create(name='Technology', slug='technology')
        writing_school, created = CourseSchool.objects.get_or_create(name='Writing', slug='writing')

        # DEVELOPMENT CODE #############################################################################################

        if settings.DEBUG:

            # USERS
            try:
                user1 = UserAccount.objects.get(email='user1@example.com')
            except UserAccount.DoesNotExist:
                user1 = UserAccount.objects.create_user('user1@example.com', 'User1 Lastname', '1q2w3e4r')
                user1.headline = 'Wood Carpenter'
                user1.phone_number = '111-1111'
                user1.save()

            try:
                user2 = UserAccount.objects.get(email='user2@example.com')
            except UserAccount.DoesNotExist:
                user2 = UserAccount.objects.create_user('user2@example.com', 'User2 Lastname', '1q2w3e4r')
                user2.headline = 'Computer Science Student'
                user2.phone_number = '222-2222'
                user2.save()

            try:
                user3 = UserAccount.objects.get(email='user3@example.com')
            except UserAccount.DoesNotExist:
                user3 = UserAccount.objects.create_user('user3@example.com', 'User3 Lastname', '1q2w3e4r')
                user3.headline = 'Avid Learner'
                user3.phone_number = '333-3333'
                user3.save()

            try:
                user4 = UserAccount.objects.get(email='user4@example.com')
            except UserAccount.DoesNotExist:
                user4 = UserAccount.objects.create_user('user4@example.com', 'User4 Lastname', '1q2w3e4r')
                user4.headline = 'Lazy One'
                user4.phone_number = '444-4444'
                user4.save()

            # VENUES

            try:
                place1 = Place.objects.get(name='Queen Sirikit National Convention Center')
            except Place.DoesNotExist:
                place1 = Place.objects.create(
                    name='Queen Sirikit National Convention Center',
                    code='QSNCC',
                    address='60 New Rachadapisek Road, Klongtoey, Bangkok 10110',
                    province_code='TH-10',
                    country='TH',
                    direction='Go to Rachadapisek',
                    latlng='13.729213,100.557818',
                    is_userdefined=False,
                )

            try:
                place2 = Place.objects.get(name='Hubba')
            except Place.DoesNotExist:
                place2 = Place.objects.create(
                    name='Hubba',
                    code='HUBBA',
                    address='19 Soi Ekkamai 4, Sukumvit 63 Rd. Prakanong Nua, Wattana Bangkok, Thailand 10110',
                    province_code='TH-10',
                    country='TH',
                    direction='Go to Ekkamai',
                    latlng='13.725378,100.587645',
                    is_userdefined=False,
                )

            try:
                place3 = Place.objects.get(name='My Home')
            except Place.DoesNotExist:
                place3 = Place.objects.create(
                    name='My Home',
                    address='233/235 Srinakarin Rd. Bang Muang, Muang, Samutprakarn 10270',
                    province_code='TH-11',
                    country='TH',
                    direction='Go to Srinakarin',
                    latlng='13.614947,100.626386',
                    is_userdefined=True,
                    created_by=user2,
                )

            # COURSES

            """
            watercolor_topic, created = CourseTopic.objects.get_or_create(name='Watercolor Painting', slug='watercolor_painting')
            computer_topic, created = CourseTopic.objects.get_or_create(name='Computer', slug='computer')
            programming_topic, created = CourseTopic.objects.get_or_create(name='Programming', slug='programming')
            django_topic, created = CourseTopic.objects.get_or_create(name='Django', slug='django')
            ux_topic, created = CourseTopic.objects.get_or_create(name='User Experience', slug='user_experience')
            web_design_topic, created = CourseTopic.objects.get_or_create(name='Web Design', slug='web_design')
            cooking_topic, created = CourseTopic.objects.get_or_create(name='Cooking', slug='cooking')
            steak_topic, created = CourseTopic.objects.get_or_create(name='Steak Cooking', slug='steak_cooking')
            building_topic, created = CourseTopic.objects.get_or_create(name='Building', slug='building')
            """

            try:
                course1 = Course.objects.get(uid='COURSE1')
            except Course.DoesNotExist:
                course1 = Course.objects.create(
                    uid='COURSE1',
                    title='How to grill steak',
                    description='I will show you how to grill steak',
                    price=500,
                    duration=6,
                    maximum_people=20,
                    prerequisites='Body',
                    place=place1,

                    teacher=user1,
                    status='PUBLISHED',
                    first_published=pytz.timezone('UTC').localize(datetime.datetime(2013, 5, 28, 8, 0), is_dst=None),
                    last_scheduled=pytz.timezone('UTC').localize(datetime.datetime(2013, 5, 28, 8, 0), is_dst=None),
                )

                course1.schools.add(culinary_arts_school)
                course1.save()

                course1_schedule1 = CourseSchedule.objects.create(
                    course=course1,
                    start_datetime=pytz.timezone('UTC').localize(datetime.datetime(2013, 6, 15, 11, 0), is_dst=None),
                    status='OPENING',
                )

                course1_schedule2 = CourseSchedule.objects.create(
                    course=course1,
                    start_datetime=pytz.timezone('UTC').localize(datetime.datetime(2013, 7, 15, 11, 0), is_dst=None),
                    status='OPENING',
                )

                enrollment1, _ = CourseEnrollment.objects.get_or_create(
                    code='ENROLL1_1',
                    student=user2,
                    schedule=course1_schedule1,
                    price=500,
                    people=1,
                    total=500,
                    payment_status='PAYMENT_RECEIVED',
                    status='CONFIRMED',
                )

                enrollment2, _ = CourseEnrollment.objects.get_or_create(
                    code='ENROLL1_2',
                    student=user3,
                    schedule=course1_schedule1,
                    price=500,
                    people=1,
                    total=500,
                    payment_status='PAYMENT_RECEIVED',
                    status='CONFIRMED',
                )

                UserAccountBalanceTransaction.objects.create(user=user1, transaction_type='RECEIVED', amount=Decimal('500'))
                UserAccountBalanceTransaction.objects.create(user=user1, transaction_type='RECEIVED', amount=Decimal('500'))

                CourseFeedback.objects.get_or_create(
                    enrollment=enrollment1,
                    content='It was awesome',
                    feelings='like,laugh',
                )

                CourseFeedback.objects.get_or_create(
                    enrollment=enrollment2,
                    content='It was ok',
                    feelings='laugh,inspiring',
                )

            try:
                course2 = Course.objects.get(uid='COURSE2')
            except Course.DoesNotExist:
                course2 = Course.objects.create(
                    uid='COURSE2',
                    title='How to write Django application',
                    description='I will show you how to write Django application',
                    price=1000,
                    duration=10,
                    maximum_people=10,
                    prerequisites='Python',
                    place=place3,

                    teacher=user2,
                    status='PUBLISHED',
                    first_published=pytz.timezone('UTC').localize(datetime.datetime(2013, 5, 28, 8, 0), is_dst=None),
                    last_scheduled=pytz.timezone('UTC').localize(datetime.datetime(2013, 5, 28, 9, 0), is_dst=None),
                )

                course2.schools.add(technology_school)
                course2.save()

                course2_schedule1 = CourseSchedule.objects.create(
                    course=course2,
                    start_datetime=pytz.timezone('UTC').localize(datetime.datetime(2013, 5, 20, 10, 0), is_dst=None),
                    status='OPENING',
                )

                course2_schedule2 = CourseSchedule.objects.create(
                    course=course2,
                    start_datetime=pytz.timezone('UTC').localize(datetime.datetime(2013, 6, 20, 10, 0), is_dst=None),
                    status='OPENING',
                )

                course2_schedule3 = CourseSchedule.objects.create(
                    course=course2,
                    start_datetime=pytz.timezone('UTC').localize(datetime.datetime(2013, 7, 20, 10, 0), is_dst=None),
                    status='OPENING',
                )

                enrollment1, _ = CourseEnrollment.objects.get_or_create(
                    code='ENROLL2_1',
                    student=user1,
                    schedule=course2_schedule1,
                    price=800,
                    people=1,
                    total=800,
                    payment_status='PAYMENT_RECEIVED',
                    status='CONFIRMED',
                    is_public=True,
                )

                enrollment2, _ = CourseEnrollment.objects.get_or_create(
                    code='ENROLL2_2',
                    student=user1,
                    schedule=course2_schedule2,
                    price=800,
                    people=1,
                    total=800,
                    payment_status='PAYMENT_RECEIVED',
                    status='CONFIRMED',
                    is_public=True,
                )

                enrollment3, _ = CourseEnrollment.objects.get_or_create(
                    code='ENROLL2_3',
                    student=user1,
                    schedule=course2_schedule3,
                    price=800,
                    people=1,
                    total=800,
                    payment_status='PAYMENT_RECEIVED',
                    status='CONFIRMED',
                    is_public=True,
                )

                CourseFeedback.objects.get_or_create(
                    enrollment=enrollment1,
                    content='It was ok',
                    is_public=True,
                )

                CourseFeedback.objects.get_or_create(
                    enrollment=enrollment2,
                    content='It was still ok',
                    is_public=True,
                )

                UserAccountBalanceTransaction.objects.create(user=user2, transaction_type='RECEIVED', amount=Decimal('800'))
                UserAccountBalanceTransaction.objects.create(user=user2, transaction_type='RECEIVED', amount=Decimal('800'))
                UserAccountBalanceTransaction.objects.create(user=user2, transaction_type='RECEIVED', amount=Decimal('800'))

            try:
                course3 = Course.objects.get(uid='COURSE3')
            except Course.DoesNotExist:
                course3 = Course.objects.create(
                    uid='COURSE3',
                    title='How to design a website',
                    description='I will show you how to design a website',
                    price=2000,
                    duration=18,
                    maximum_people=15,
                    place=place2,

                    teacher=user3,
                    status='PUBLISHED',
                    first_published=pytz.timezone('UTC').localize(datetime.datetime(2013, 5, 28, 8, 0), is_dst=None),
                    last_scheduled=pytz.timezone('UTC').localize(datetime.datetime(2013, 5, 28, 10, 0), is_dst=None),
                )

                course3.schools.add(technology_school)
                course3.save()

                course3_schedule1 = CourseSchedule.objects.create(
                    course=course3,
                    start_datetime=pytz.timezone('UTC').localize(datetime.datetime(2013, 7, 20, 9, 30), is_dst=None),
                    status='OPENING',
                )

                CourseEnrollment.objects.get_or_create(
                    code='ENROLL3',
                    student=user1,
                    schedule=course3_schedule1,
                    price=2000,
                    people=1,
                    total=2000,
                    payment_status='PAYMENT_RECEIVED',
                    status='CONFIRMED',
                )

                UserAccountBalanceTransaction.objects.create(user=user3, transaction_type='RECEIVED', amount=Decimal('2000'))

            try:
                course4 = Course.objects.get(uid='COURSE4')
            except Course.DoesNotExist:
                course4 = Course.objects.create(
                    uid='COURSE4',
                    title='How to build a house',
                    description='I will show you how to build a house',
                    price=6000,
                    duration=24,
                    maximum_people=4,
                    prerequisites='Saw',
                    place=place1,

                    teacher=user1,
                    status='PUBLISHED',
                    first_published=pytz.timezone('UTC').localize(datetime.datetime(2013, 5, 28, 8, 0), is_dst=None),
                    last_scheduled=pytz.timezone('UTC').localize(datetime.datetime(2013, 5, 28, 11, 0), is_dst=None),
                )

                course4.schools.add(craftmanship_school)
                course4.save()

                course4_schedule1 = CourseSchedule.objects.create(
                    course=course4,
                    start_datetime=pytz.timezone('UTC').localize(datetime.datetime(2013, 6, 30, 8, 0), is_dst=None),
                    status='OPENING',
                )
