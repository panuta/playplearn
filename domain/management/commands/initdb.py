# -*- encoding: utf-8 -*-

import datetime
from decimal import Decimal
import pytz

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand

from domain.models import WorkshopTopic, Workshop, Place, UserAccount

from reservation import functions as reservation_functions
from reservation.models import Reservation, BalanceTransaction


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

        craftmanship_topic, _ = WorkshopTopic.objects.get_or_create(name='Craftmanship', slug='craftmanship', description='Craftmanship is craftmanship')
        culinary_arts_topic, _ = WorkshopTopic.objects.get_or_create(name='Culinary Arts', slug='culinary_arts', description='Culinary Arts is culinary arts')
        design_topic, _ = WorkshopTopic.objects.get_or_create(name='Design', slug='design', description='Design is design')
        entrepreneurship_topic, _ = WorkshopTopic.objects.get_or_create(name='Entrepreneurship', slug='entrepreneurship', description='Entrepreneurship is entrepreneurship')
        fashion_and_style_topic, _ = WorkshopTopic.objects.get_or_create(name='Fashion & Style', slug='fashion_and_style', description='Fashion & Style is fashion & style')
        gardening_topic, _ = WorkshopTopic.objects.get_or_create(name='Gardening', slug='gardening', description='Gardening is gardening')
        photography_topic, _ = WorkshopTopic.objects.get_or_create(name='Photography', slug='photography', description='Photography is photography')
        technology_topic, _ = WorkshopTopic.objects.get_or_create(name='Technology', slug='technology', description='Technology is technology')
        writing_topic, _ = WorkshopTopic.objects.get_or_create(name='Writing', slug='writing', description='Writing is writing')

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
                workshop1 = Workshop.objects.get(uid='1111111111')
            except Workshop.DoesNotExist:
                workshop1 = Workshop.objects.create(
                    uid='1111111111',
                    title=u'ถ่ายรูปและแต่งรูปอย่างไรให้อวดเพื่อนได้ไม่อายใคร',
                    short_description=u'คาวบอยควีนโอเวอร์เมจิคแอพพริคอทแพนงเชิญ ลิสต์โก๊ะ ตอกย้ำ คอนแทคฟรุตม็อบสปอต เซ็นเซอร์จิ๊กซอว์ โบรกเกอร์',
                    description='I will show you how to take a photo',
                    default_price=200,
                    duration=6,
                    default_capacity=8,
                    prerequisites='a camera',
                    place=hubba_place,

                    teacher=user_panuta,
                    status=Workshop.STATUS_PUBLISHED,
                    date_published=pytz.timezone('UTC').localize(datetime.datetime(2013, 6, 1, 8, 0), is_dst=None),
                )

                workshop1.topics.add(photography_topic)
                workshop1.save()

                schedule1 = reservation_functions.create_schedule(workshop1, pytz.timezone('UTC').localize(datetime.datetime(2013, 8, 15, 9, 0), is_dst=None), workshop1.default_price, workshop1.default_capacity)
                schedule2 = reservation_functions.create_schedule(workshop1, pytz.timezone('UTC').localize(datetime.datetime(2013, 9, 1, 9, 0), is_dst=None), workshop1.default_price, workshop1.default_capacity)
                schedule3 = reservation_functions.create_schedule(workshop1, pytz.timezone('UTC').localize(datetime.datetime(2013, 9, 12, 9, 0), is_dst=None), workshop1.default_price, workshop1.default_capacity)

                reservation1 = Reservation.objects.create(
                    code='ENROLL1_1',
                    user=user4,
                    schedule=schedule1,
                    price=200,
                    seats=2,
                    total=400,
                    status=Reservation.STATUS_CONFIRMED,
                    payment_status=Reservation.PAYMENT_STATUS_PAID,
                )

                reservation2 = Reservation.objects.create(
                    code='ENROLL1_2',
                    user=user2,
                    schedule=schedule2,
                    price=200,
                    seats=1,
                    total=200,
                    status=Reservation.STATUS_CONFIRMED,
                    payment_status=Reservation.PAYMENT_STATUS_PAID,
                )

                reservation3 = Reservation.objects.create(
                    code='ENROLL1_3',
                    user=user3,
                    schedule=schedule2,
                    price=200,
                    seats=3,
                    total=600,
                    status=Reservation.STATUS_CONFIRMED,
                    payment_status=Reservation.PAYMENT_STATUS_PAID,
                )

                reservation4 = Reservation.objects.create(
                    code='ENROLL1_4',
                    user=user4,
                    schedule=schedule2,
                    price=200,
                    seats=1,
                    total=200,
                    status=Reservation.STATUS_CONFIRMED,
                    payment_status=Reservation.PAYMENT_STATUS_PAID,
                )

                BalanceTransaction.objects.create(user=user_panuta, transaction_type=BalanceTransaction.RECEIVED_TRANSACTION, amount=Decimal('400'), reservation=reservation1)
                BalanceTransaction.objects.create(user=user_panuta, transaction_type=BalanceTransaction.RECEIVED_TRANSACTION, amount=Decimal('200'), reservation=reservation2)
                BalanceTransaction.objects.create(user=user_panuta, transaction_type=BalanceTransaction.RECEIVED_TRANSACTION, amount=Decimal('600'), reservation=reservation3)
                BalanceTransaction.objects.create(user=user_panuta, transaction_type=BalanceTransaction.RECEIVED_TRANSACTION, amount=Decimal('200'), reservation=reservation4)

            try:
                workshop2 = Workshop.objects.get(uid='2222222222')
            except Workshop.DoesNotExist:
                workshop2 = Workshop.objects.create(
                    uid='2222222222',
                    title=u'ทำสวนผักสำหรับคนเมือง',
                    short_description=u'วิลล์สวีทเอ็นจีโอ ไฮแจ็คสเตอริโอ สุริยยาตร์ม้าหินอ่อนแต๋วสตาร์รุสโซแทงโก้ มยุราภิรมย์ว้าวเบนโตะแฟกซ์แคร็กเกอร์',
                    description='I will show you how to grow a plant',
                    default_price=400,
                    duration=8,
                    default_capacity=10,
                    place=home_place,

                    teacher=user2,
                    status=Workshop.STATUS_PUBLISHED,
                    date_published=pytz.timezone('UTC').localize(datetime.datetime(2013, 5, 28, 8, 0), is_dst=None),
                )

                workshop2.topics.add(gardening_topic)
                workshop2.save()

                schedule1 = reservation_functions.create_schedule(workshop2, pytz.timezone('UTC').localize(datetime.datetime(2013, 8, 15, 10, 0), is_dst=None), workshop2.default_price, workshop2.default_capacity)
                schedule2 = reservation_functions.create_schedule(workshop2, pytz.timezone('UTC').localize(datetime.datetime(2013, 9, 1, 10, 0), is_dst=None), workshop2.default_price, workshop2.default_capacity)
                schedule3 = reservation_functions.create_schedule(workshop2, pytz.timezone('UTC').localize(datetime.datetime(2013, 9, 30, 10, 0), is_dst=None), workshop2.default_price, workshop2.default_capacity)

                reservation4 = Reservation.objects.create(
                    code='ENROLL2_1',
                    user=user4,
                    schedule=schedule2,
                    price=200,
                    seats=1,
                    total=200,
                    status=Reservation.STATUS_CONFIRMED,
                    payment_status=Reservation.PAYMENT_STATUS_PAID,
                    )

                reservation1 = Reservation.objects.create(
                    code='ENROLL2_2',
                    user=user_panuta,
                    schedule=schedule1,
                    price=400,
                    seats=2,
                    total=800,
                    status=Reservation.STATUS_CONFIRMED,
                    payment_status=Reservation.PAYMENT_STATUS_PAID,
                )

                reservation2 = Reservation.objects.create(
                    code='ENROLL2_3',
                    user=user4,
                    schedule=schedule1,
                    price=400,
                    seats=1,
                    total=400,
                    status=Reservation.STATUS_CONFIRMED,
                    payment_status=Reservation.PAYMENT_STATUS_PAID,
                )

                reservation3 = Reservation.objects.create(
                    code='ENROLL2_4',
                    user=user_panuta,
                    schedule=schedule2,
                    price=400,
                    seats=1,
                    total=400,
                    status=Reservation.STATUS_CONFIRMED,
                    payment_status=Reservation.PAYMENT_STATUS_PAID,
                )

                BalanceTransaction.objects.create(user=user2, transaction_type=BalanceTransaction.RECEIVED_TRANSACTION, amount=Decimal('800'), reservation=reservation1)
                BalanceTransaction.objects.create(user=user2, transaction_type=BalanceTransaction.RECEIVED_TRANSACTION, amount=Decimal('400'), reservation=reservation2)
                BalanceTransaction.objects.create(user=user2, transaction_type=BalanceTransaction.RECEIVED_TRANSACTION, amount=Decimal('400'), reservation=reservation3)
