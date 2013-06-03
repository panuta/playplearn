# -*- encoding: utf-8 -*-

import datetime
import decimal
import random
from django.core.urlresolvers import reverse
import shortuuid

from django.conf import settings
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db import models
from django.db.models import Q, Count, Sum
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.crypto import salted_hmac
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from easy_thumbnails.fields import ThumbnailerImageField
from easy_thumbnails.files import get_thumbnailer

from common.constants.common import GENDER_CHOICES
from common.constants.course import *
from common.constants.currency import CURRENCY_CHOICES
from common.constants.transaction import TRANSACTION_TYPE_CHOICES
from common.email import send_registration_email

SHORTUUID_ALPHABETS_FOR_ID = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'


# ACCOUNT ##############################################################################################################

class UserAccountManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError(_('Users must have an email address'))

        if not name:
            raise ValueError(_('Users must have a name'))

        user = UserAccount.objects.create(
            email=UserAccountManager.normalize_email(email),
            name=name,
        )

        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, name, password):
        user = self.create_user(email, name, password)
        user.is_admin = True
        user.save()
        return user


def user_avatar_dir(instance, filename):
    return 'users/%s/%s' % (instance.uid, filename)


class UserAccount(AbstractBaseUser):
    uid = models.CharField(max_length=50, unique=True, db_index=True)
    email = models.EmailField(max_length=255, unique=True, db_index=True)

    name = models.CharField(max_length=300)
    headline = models.CharField(max_length=300, blank=True)
    avatar = ThumbnailerImageField(upload_to=user_avatar_dir, blank=True, null=True)
    phone_number = models.CharField(max_length=100, blank=True)
    website = models.CharField(max_length=255, blank=True)

    date_joined = models.DateTimeField(default=timezone.now())
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def save(self, *args, **kwargs):
        if not self.uid:
            uuid = None

            while not uuid:
                shortuuid.set_alphabet(SHORTUUID_ALPHABETS_FOR_ID)
                uuid = shortuuid.uuid()[:10]

                try:
                    UserAccount.objects.get(uid=uuid)
                except UserAccount.DoesNotExist:
                    pass
                else:
                    uuid = None

            self.uid = uuid

        models.Model.save(self, *args, **kwargs)

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        if ' ' in self.name:
            return self.name.split(' ')[0]
        return self.name

    def __unicode__(self):
        return '%s <%s>' % (self.name, self.email)

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        return self.is_admin

    # Avatars

    @property
    def normal_avatar_url(self):
        if self.avatar:
            return get_thumbnailer(self.avatar)['avatar_normal'].url
        return '%simages/%s' % (settings.STATIC_URL, settings.USER_AVATAR_DEFAULT_NORMAL)

    @property
    def small_avatar_url(self):
        if self.avatar:
            return get_thumbnailer(self.avatar)['avatar_small'].url
        return '%simages/%s' % (settings.STATIC_URL, settings.USER_AVATAR_DEFAULT_SMALL)

    @property
    def smaller_avatar_url(self):
        if self.avatar:
            return get_thumbnailer(self.avatar)['avatar_smaller'].url
        return '%simages/%s' % (settings.STATIC_URL, settings.USER_AVATAR_DEFAULT_SMALLER)

    @property
    def tiny_avatar_url(self):
        if self.avatar:
            return get_thumbnailer(self.avatar)['avatar_tiny'].url
        return '%simages/%s' % (settings.STATIC_URL, settings.USER_AVATAR_DEFAULT_TINY)

    # Stats ------------------------------------------------------------------------------------------------------------

    def stats_upcoming_courses(self):
        rightnow = now()
        return CourseSchedule.objects \
            .filter(status='OPENING', start_datetime__gt=rightnow) \
            .filter((Q(course__teacher=self) & Q(course__status='PUBLISHED') & Q(status='OPENING'))
                    | Q(reservations__student__in=(self,))).count()

    def stats_courses_teaching(self):
        return Course.objects.filter(
            teacher=self,
            status='PUBLISHED'
        ).count()

    def stats_classes_teaching(self):
        return CourseSchedule.objects.filter(course__teacher=self, course__status='PUBLISHED', status='OPENING').count()

    def stats_students_teaching(self):
        return UserAccount.objects.filter(reservations__schedule__course__teacher=self, reservations__status='CONFIRMED', reservations__schedule__status='OPENING').distinct().count()

    def stats_courses_attended(self):
        rightnow = now()
        return Course.objects.filter(
            schedules__start_datetime__lte=rightnow,
            schedules__reservations__status='CONFIRMED',
            schedules__reservations__student=self,
        ).count()

    def stats_feedbacks_received(self):
        return CourseFeedback.objects.filter(reservation__schedule__course__teacher=self).count()

    def stats_positive_feedbacks_percentage(self):
        total = self.stats_feedbacks_received()
        return float(CourseFeedback.objects.filter(reservation__schedule__course__teacher=self, is_positive=True).count()) / float(total) * 100 if total else 0

    def stats_feedbacks_given(self):
        return self.feedbacks.count()

    def stats_total_earning(self):
        total_earning = UserAccountBalanceTransaction.objects.filter(transaction_type='RECEIVED').aggregate(Sum('amount'))['amount__sum']
        return total_earning if total_earning else 0


class UserRegistrationManager(models.Manager):
    def create_registration(self, email):
        key_salt = 'account.models.UserRegistrationManager_%d' % random.randint(1, 99999999)
        email = email.encode('utf-8')
        value = email
        registration_key = salted_hmac(key_salt, value).hexdigest()

        return self.create(email=email, registration_key=registration_key)


class UserRegistration(models.Model):
    email = models.CharField(max_length=254)
    registration_key = models.CharField(max_length=200, unique=True, db_index=True)
    registered = models.DateTimeField(auto_now_add=True)

    objects = UserRegistrationManager()

    def __unicode__(self):
        return '%s [%s]' % (self.email, self.registration_key)

    def send_confirmation_email(self):
        email_context = {'settings': settings, 'registration': self}

        subject = _('LearningWolf Registration Confirmation')
        text_email_body = render_to_string('account/emails/registration_confirmation.txt', email_context)
        html_email_body = render_to_string('account/emails/registration_confirmation.html', email_context)

        send_registration_email([self.email], subject, text_email_body, html_email_body)

        return True

    def claim_registration(self, name, password):
        user_account = UserAccount.objects.create_user(self.email, name, password)
        return user_account


class UserAccountBalance(models.Model):
    user = models.OneToOneField(UserAccount, related_name='account_balance')
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=decimal.Decimal('0'))
    last_modified = models.DateTimeField(auto_now=True)


class UserAccountBalanceTransaction(models.Model):
    user = models.ForeignKey(UserAccount, related_name='balance_transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.CharField(max_length=500, blank=True)
    created = models.DateTimeField(auto_now_add=True)


# VENUE ################################################################################################################

class Venue(models.Model):
    name = models.CharField(max_length=500)
    code = models.CharField(max_length=100, blank=True, db_index=True)
    address = models.CharField(max_length=1000)
    province_code = models.CharField(max_length=100)
    country = models.CharField(max_length=5)
    phone_number = models.CharField(max_length=50, blank=True)
    direction = models.TextField(blank=True)
    latlng = models.CharField(max_length=50)
    is_userdefined = models.BooleanField()
    is_visible = models.BooleanField(default=True)

    @property
    def venue_url(self):
        if self.code:
            return reverse('view_venue_info_by_code', args=(self.code,))
        return reverse('view_venue_info_by_id', args=(self.id,))


class VenueDetail(models.Model):
    venue = models.ForeignKey(Venue, related_name='details')
    detail_name = models.CharField(max_length=100)
    detail_value = models.CharField(max_length=500)


# COURSE ###############################################################################################################

class CourseSchool(models.Model):
    slug = models.CharField(max_length=300)
    name = models.CharField(max_length=300)


class CourseTopic(models.Model):
    slug = models.CharField(max_length=300)
    name = models.CharField(max_length=300)


class CourseManager(models.Manager):
    use_for_related_fields = True

    def get_query_set(self):
        return super(CourseManager, self).get_query_set().exclude(status='DELETED')


def course_cover_dir(instance, filename):
    return 'users/%s/courses/%s/%s' % (instance.teacher.uid, instance.uid, filename)


def course_picture_dir(instance, filename):
    return 'users/%s/courses/%s/%s' % (instance.teacher.uid, instance.uid, filename)


class Course(models.Model):
    uid = models.CharField(max_length=50, db_index=True)
    title = models.CharField(max_length=500)
    cover = ThumbnailerImageField(upload_to=course_cover_dir, null=True)
    description = models.TextField(blank=True)
    schools = models.ManyToManyField(CourseSchool, null=True)
    topics = models.ManyToManyField(CourseTopic, null=True)

    venue = models.ForeignKey(Venue, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_unit = models.CharField(max_length=20, default='THB', choices=CURRENCY_CHOICES)
    duration = models.PositiveSmallIntegerField(null=True, blank=True)
    maximum_people = models.PositiveSmallIntegerField(null=True, blank=True)
    level = models.CharField(max_length=20, choices=COURSE_LEVEL_CHOICES, blank=True)
    prerequisites = models.CharField(max_length=500, blank=True)

    teacher = models.ForeignKey(UserAccount, related_name='courses')
    credentials = models.CharField(max_length=2000, blank=True)

    next_schedule = models.ForeignKey('CourseSchedule', null=True, related_name='parent_course')

    status = models.CharField(max_length=20, choices=COURSE_STATUS_CHOICES, default='DRAFT')
    created = models.DateTimeField(auto_now_add=True)
    first_published = models.DateTimeField(null=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['-created']

    objects = CourseManager()

    def save(self, *args, **kwargs):
        shortuuid.set_alphabet('1234567890')
        if not self.uid:
            temp_uuid = shortuuid.uuid()[0:10]
            while Course.objects.filter(uid=temp_uuid).exists():
                temp_uuid = shortuuid.uuid()[0:10]
            self.uid = temp_uuid
        super(Course, self).save(*args, **kwargs)

    # PROPERTIES -------------------------------------------------------------------------------------------------------

    def cover_url(self):
        if self.cover:
            return get_thumbnailer(self.cover)['course_cover_normal'].url
        return '%simages/%s' % (settings.STATIC_URL, settings.COURSE_COVER_DEFAULT_NORMAL)

    def small_cover_url(self):
        if self.cover:
            return get_thumbnailer(self.cover)['course_cover_small'].url
        return '%simages/%s' % (settings.STATIC_URL, settings.COURSE_COVER_DEFAULT_SMALL)

    def status_name(self):
        return COURSE_STATUS_MAP[self.status]['name']

    # PERMISSIONS ------------------------------------------------------------------------------------------------------

    def can_view(self, user):
        return (self.status == 'PUBLISHED') or (self.status == 'UNPUBLISHED' and user == self.teacher) or \
               (self.status == 'WAIT_FOR_APPROVAL' and (user == self.teacher or user.is_staff()))

    def can_add_new_class(self):
        rightnow = now()
        return self.status == 'PUBLISHED' and self.next_schedule.start_datetime <= rightnow

    # STATS ------------------------------------------------------------------------------------------------------------

    def stats_attended_students(self):
        return UserAccount.objects.filter(reservations__schedule__course=self).distinct().count()

    def stats_feedbacks(self):
        return CourseFeedback.objects.filter(reservation__schedule__course=self).count()


class CourseOutline(models.Model):
    course = models.ForeignKey(Course, related_name='outlines')
    title = models.CharField(max_length=500)
    description = models.CharField(max_length=1000, null=True, blank=True, default='')


class CoursePicture(models.Model):
    course = models.ForeignKey(Course, related_name='pictures')
    image = ThumbnailerImageField(upload_to=course_picture_dir)
    ordering = models.PositiveIntegerField(default=0)
    uploaded = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['ordering']


class CourseScheduleManager(models.Manager):
    use_for_related_fields = True

    def get_query_set(self):
        return super(CourseScheduleManager, self).get_query_set().exclude(status='DELETED')


class CourseSchedule(models.Model):
    course = models.ForeignKey(Course, related_name='schedules')
    start_datetime = models.DateTimeField()
    status = models.CharField(max_length=30, default='OPENING', choices=COURSE_SCHEDULE_STATUS_CHOICES)

    class Meta:
        ordering = ['-start_datetime']

    objects = CourseScheduleManager()

    def is_opening(self):
        rightnow = now()
        return self.status == 'OPENING' and self.start_datetime > rightnow

    # STATS ############################################################################################################

    def stats_seats_reserved(self):
        return CourseReservation.objects.filter(schedule=self, status='CONFIRMED').count()

    def stats_seats_left(self):
        return self.course.maximum_people - self.stats_seats_reserved()


class CourseReservation(models.Model):
    code = models.CharField(max_length=20, db_index=True)
    student = models.ForeignKey(UserAccount, related_name='reservations')
    schedule = models.ForeignKey(CourseSchedule, related_name='reservations')
    note = models.CharField(max_length=1000, blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=30, choices=COURSE_RESERVATION_PAYMENT_STATUS_CHOICES)

    status = models.CharField(max_length=20, choices=COURSE_RESERVATION_STATUS_CHOICES)
    status_reason = models.CharField(max_length=100, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-schedule__start_datetime']

    def has_feedback(self):
        return CourseFeedback.objects.filter(reservation=self).exists()


class CourseFeedback(models.Model):
    user = models.ForeignKey(UserAccount, related_name='feedbacks')
    reservation = models.OneToOneField('CourseReservation', related_name='feedback')
    content = models.CharField(max_length=2000)
    is_positive = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)

