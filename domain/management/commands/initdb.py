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

        craftmanship_school, _ = CourseSchool.objects.get_or_create(name='Craftmanship', slug='craftmanship', description='Craftmanship is craftmanship')
        culinary_arts_school, _ = CourseSchool.objects.get_or_create(name='Culinary Arts', slug='culinary_arts', description='Culinary Arts is culinary arts')
        design_school, _ = CourseSchool.objects.get_or_create(name='Design', slug='design', description='Design is design')
        entrepreneurship_school, _ = CourseSchool.objects.get_or_create(name='Entrepreneurship', slug='entrepreneurship', description='Entrepreneurship is entrepreneurship')
        fashion_and_style_school, _ = CourseSchool.objects.get_or_create(name='Fashion & Style', slug='fashion_and_style', description='Fashion & Style is fashion & style')
        gardening_school, _ = CourseSchool.objects.get_or_create(name='Gardening', slug='gardening', description='Gardening is gardening')
        photography_school, _ = CourseSchool.objects.get_or_create(name='Photography', slug='photography', description='Photography is photography')
        technology_school, _ = CourseSchool.objects.get_or_create(name='Technology', slug='technology', description='Technology is technology')
        writing_school, _ = CourseSchool.objects.get_or_create(name='Writing', slug='writing', description='Writing is writing')

        # DEVELOPMENT CODE #############################################################################################

        if settings.DEBUG:

            # USERS
            try:
                user_panuta = UserAccount.objects.get(email='panuta@example.com')
            except UserAccount.DoesNotExist:
                user_panuta = UserAccount.objects.create_user('panuta@example.com', u'ภาณุ ตั้งเฉลิมกุล', '1q2w3e4r')
                user_panuta.headline = u'ปัญหาของผมคือการอยากทำไปหมดซะทุกสิ่ง'
                user_panuta.phone_number = '089-111-1111'
                user_panuta.save()

            try:
                user1 = UserAccount.objects.get(email='user1@example.com')
            except UserAccount.DoesNotExist:
                user1 = UserAccount.objects.create_user('user1@example.com', u'สมควร แก่การเรียน', '1q2w3e4r')
                user1.headline = u'เด็กคอมสายแข็ง'
                user1.phone_number = '085-222-2222'
                user1.save()

            try:
                user2 = UserAccount.objects.get(email='user2@example.com')
            except UserAccount.DoesNotExist:
                user2 = UserAccount.objects.create_user('user2@example.com', u'หญิงเล็ก ช่างจินตนาการ', '1q2w3e4r')
                user2.headline = u'กราฟฟิคดีไซน์เนอร์'
                user2.phone_number = '096-333-3333'
                user2.save()

            try:
                user3 = UserAccount.objects.get(email='user3@example.com')
            except UserAccount.DoesNotExist:
                user3 = UserAccount.objects.create_user('user3@example.com', u'เด็กช่าง (สงสัย)', '1q2w3e4r')
                user3.headline = u'คำถามสำคัญกว่าคำตอบ'
                user3.phone_number = '084-444-4444'
                user3.save()

            try:
                user4 = UserAccount.objects.get(email='user4@example.com')
            except UserAccount.DoesNotExist:
                user4 = UserAccount.objects.create_user('user4@example.com', u'ผู้ใหญ่ใจดี', '1q2w3e4r')
                user4.headline = u'ใจดีจริงๆ นะเด็กๆ'
                user4.phone_number = '084-555-5555'
                user4.save()

            # VENUES

            try:
                qsncc_place = Place.objects.get(name='Queen Sirikit National Convention Center')
            except Place.DoesNotExist:
                qsncc_place = Place.objects.create(
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
                hubba_place = Place.objects.get(name='Hubba')
            except Place.DoesNotExist:
                hubba_place = Place.objects.create(
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
                home_place = Place.objects.get(name=u'บ้านเลขที่ 233/235')
            except Place.DoesNotExist:
                home_place = Place.objects.create(
                    name=u'บ้านเลขที่ 233/235',
                    address='233/235 หมู่บ้านนันทวัน ถ.ศรีนครินทร์ ต.บางเมือง อ.เมือง',
                    province_code='TH-11',
                    country='TH',
                    direction='Go to Srinakarin',
                    latlng='13.614947,100.626386',
                    is_userdefined=True,
                    created_by=user2,
                )

            try:
                od_place = Place.objects.get(name='Opendream')
            except Place.DoesNotExist:
                od_place = Place.objects.create(
                    name='Opendream',
                    address=u'299/92 ถ.สุทธิสารวินิจฉัย แขวงสามเสนนอก เขตห้วยขวาง',
                    province_code='TH-10',
                    country='TH',
                    direction=u'จากถนนพระราม 9 เลี้ยวเข้ามารัชดาภิเษกทางที่จะไปลาดพร้าว ตรงมาเรื่อยๆ จนเจอสี่แยกสุทธิสาร เลี้ยวขวาแล้วขับตรงเข้ามาเรื่อยๆ',
                    latlng='13.791149,100.5882',
                    is_userdefined=True,
                    created_by=user2,
                )

            # COURSES

            try:
                course1 = Course.objects.get(uid='1111111111')
            except Course.DoesNotExist:
                course1 = Course.objects.create(
                    uid='1111111111',
                    title=u'ถ่ายรูปและแต่งรูปอย่างไรให้อวดเพื่อนได้ไม่อายใคร',
                    description='I will show you how to take a photo',
                    price=200,
                    duration=6,
                    maximum_people=8,
                    prerequisites='a camera',
                    place=hubba_place,

                    teacher=user_panuta,
                    status='PUBLISHED',
                    first_published=pytz.timezone('UTC').localize(datetime.datetime(2013, 6, 1, 8, 0), is_dst=None),
                    last_scheduled=pytz.timezone('UTC').localize(datetime.datetime(2013, 8, 23, 8, 0), is_dst=None),
                )

                course1.schools.add(photography_school)
                course1.save()

                course1_schedule1 = CourseSchedule.objects.create(
                    course=course1,
                    start_datetime=pytz.timezone('UTC').localize(datetime.datetime(2013, 8, 15, 9, 0), is_dst=None),
                    status='OPENING',
                )

                course1_schedule2 = CourseSchedule.objects.create(
                    course=course1,
                    start_datetime=pytz.timezone('UTC').localize(datetime.datetime(2013, 9, 1, 9, 0), is_dst=None),
                    status='OPENING',
                )

                course1_schedule3 = CourseSchedule.objects.create(
                    course=course1,
                    start_datetime=pytz.timezone('UTC').localize(datetime.datetime(2013, 9, 12, 9, 0), is_dst=None),
                    status='OPENING',
                )

                enrollment1, _ = CourseEnrollment.objects.get_or_create(
                    code='ENROLL1_1',
                    student=user4,
                    schedule=course1_schedule1,
                    price=200,
                    people=2,
                    total=400,
                    payment_status='PAYMENT_RECEIVED',
                    status='CONFIRMED',
                )

                enrollment2, _ = CourseEnrollment.objects.get_or_create(
                    code='ENROLL1_2',
                    student=user2,
                    schedule=course1_schedule2,
                    price=200,
                    people=1,
                    total=200,
                    payment_status='PAYMENT_RECEIVED',
                    status='CONFIRMED',
                )

                enrollment3, _ = CourseEnrollment.objects.get_or_create(
                    code='ENROLL1_3',
                    student=user3,
                    schedule=course1_schedule2,
                    price=200,
                    people=3,
                    total=600,
                    payment_status='PAYMENT_RECEIVED',
                    status='CONFIRMED',
                )

                enrollment4, _ = CourseEnrollment.objects.get_or_create(
                    code='ENROLL1_4',
                    student=user4,
                    schedule=course1_schedule2,
                    price=200,
                    people=1,
                    total=200,
                    payment_status='PAYMENT_RECEIVED',
                    status='CONFIRMED',
                )

                UserAccountBalanceTransaction.objects.create(user=user1, transaction_type='RECEIVED', amount=Decimal('400'), enrollment=enrollment1)
                UserAccountBalanceTransaction.objects.create(user=user1, transaction_type='RECEIVED', amount=Decimal('200'), enrollment=enrollment2)
                UserAccountBalanceTransaction.objects.create(user=user1, transaction_type='RECEIVED', amount=Decimal('600'), enrollment=enrollment3)
                UserAccountBalanceTransaction.objects.create(user=user1, transaction_type='RECEIVED', amount=Decimal('200'), enrollment=enrollment4)

            try:
                course2 = Course.objects.get(uid='2222222222')
            except Course.DoesNotExist:
                course2 = Course.objects.create(
                    uid='2222222222',
                    title=u'ทำสวนผักสำหรับคนเมือง',
                    description='I will show you how to grow a plant',
                    price=400,
                    duration=8,
                    maximum_people=10,
                    place=home_place,

                    teacher=user2,
                    status='PUBLISHED',
                    first_published=pytz.timezone('UTC').localize(datetime.datetime(2013, 5, 28, 8, 0), is_dst=None),
                    last_scheduled=pytz.timezone('UTC').localize(datetime.datetime(2013, 6, 15, 9, 0), is_dst=None),
                )

                course2.schools.add(gardening_school)
                course2.save()

                course2_schedule1 = CourseSchedule.objects.create(
                    course=course2,
                    start_datetime=pytz.timezone('UTC').localize(datetime.datetime(2013, 8, 15, 10, 0), is_dst=None),
                    status='OPENING',
                )

                course2_schedule2 = CourseSchedule.objects.create(
                    course=course2,
                    start_datetime=pytz.timezone('UTC').localize(datetime.datetime(2013, 9, 1, 10, 0), is_dst=None),
                    status='CANCELLED',
                )

                course2_schedule2 = CourseSchedule.objects.create(
                    course=course2,
                    start_datetime=pytz.timezone('UTC').localize(datetime.datetime(2013, 9, 30, 10, 0), is_dst=None),
                    status='OPENING',
                )

                enrollment1, _ = CourseEnrollment.objects.get_or_create(
                    code='ENROLL2_1',
                    student=user_panuta,
                    schedule=course2_schedule1,
                    price=400,
                    people=2,
                    total=800,
                    payment_status='PAYMENT_RECEIVED',
                    status='CONFIRMED',
                    is_public=True,
                )

                enrollment2, _ = CourseEnrollment.objects.get_or_create(
                    code='ENROLL2_2',
                    student=user4,
                    schedule=course2_schedule1,
                    price=400,
                    people=1,
                    total=400,
                    payment_status='PAYMENT_RECEIVED',
                    status='CONFIRMED',
                    is_public=True,
                )

                enrollment3, _ = CourseEnrollment.objects.get_or_create(
                    code='ENROLL2_3',
                    student=user_panuta,
                    schedule=course2_schedule2,
                    price=400,
                    people=1,
                    total=400,
                    payment_status='PAYMENT_RECEIVED',
                    status='CONFIRMED',
                    is_public=True,
                )

                UserAccountBalanceTransaction.objects.create(user=user2, transaction_type='RECEIVED', amount=Decimal('800'), enrollment=enrollment1)
                UserAccountBalanceTransaction.objects.create(user=user2, transaction_type='RECEIVED', amount=Decimal('400'), enrollment=enrollment2)
                UserAccountBalanceTransaction.objects.create(user=user2, transaction_type='RECEIVED', amount=Decimal('400'), enrollment=enrollment3)
