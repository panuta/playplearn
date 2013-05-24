# -*- encoding: utf-8 -*-

import datetime
import decimal
import random
import shortuuid

from django.conf import settings
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db import models
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.crypto import salted_hmac
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from easy_thumbnails.fields import ThumbnailerImageField
from easy_thumbnails.files import get_thumbnailer

from common.constants.common import GENDER_CHOICES
from common.constants.course import *
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
    headline = models.CharField(max_length=300, null=True, blank=True, default='')
    avatar = ThumbnailerImageField(upload_to=user_avatar_dir, blank=True, null=True)

    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True, default='')
    age = models.PositiveSmallIntegerField(null=True)

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
    def tiny_avatar_url(self):
        if self.avatar:
            return get_thumbnailer(self.avatar)['avatar_tiny'].url
        return '%simages/%s' % (settings.STATIC_URL, settings.USER_AVATAR_DEFAULT_TINY)

    # Stats ------------------------------------------------------------------------------------------------------------

    def num_of_upcoming_courses(self):
        rightnow = now()
        return CourseSchedule.objects \
            .filter(status='OPENING', start_datetime__gt=rightnow) \
            .filter((Q(course__teacher=self) & Q(course__status='PUBLISHED') & Q(status='OPENING'))
                    | Q(enrollments__student__in=(self,))).count()

    def num_of_courses_teaching(self):
        return Course.objects.filter(
            teacher=self,
            status='PUBLISHED'
        ).count()

    def num_of_courses_attended(self):
        rightnow = now()
        return Course.objects.filter(
            schedules__start_datetime__lte=rightnow,
            schedules__enrollments__status='CONFIRMED',
            schedules__enrollments__student=self,
        ).count()

    def num_of_reviews_received(self):
        return CourseReview.objects.filter(enrollment__schedule__course__teacher=self).count()

    def num_of_reviews_written(self):
        return self.reviews.count()


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
    note = models.CharField(max_length=500, null=True, blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)


# VENUE ################################################################################################################

class Venue(models.Model):
    name = models.CharField(max_length=500)
    address = models.CharField(max_length=1000)
    province = models.SmallIntegerField(default=0)
    latlng = models.CharField(max_length=50)


class VenueDetail(models.Model):
    venue = models.ForeignKey(Venue, related_name='details')
    detail_name = models.CharField(max_length=100)
    detail_value = models.CharField(max_length=500)


# COURSE ###############################################################################################################

class CourseSchool(models.Model):
    name = models.CharField(max_length=300)


class CourseTopic(models.Model):
    name = models.CharField(max_length=500)


class CourseManager(models.Manager):
    use_for_related_fields = True

    def get_query_set(self):
        return super(CourseManager, self).get_query_set().exclude(status='DELETED')


class Course(models.Model):
    uid = models.CharField(max_length=50, db_index=True)
    title = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True, default='')
    schools = models.ManyToManyField(CourseSchool, null=True, blank=True)
    topics = models.ManyToManyField(CourseTopic, null=True, blank=True)
    tuition_fees = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    duration = models.PositiveSmallIntegerField(null=True)
    duration_unit = models.CharField(max_length=10, null=True, blank=True, default='HOURS')
    minimum_people = models.PositiveSmallIntegerField(null=True)
    maximum_people = models.PositiveSmallIntegerField(null=True)
    level = models.CharField(max_length=20, choices=COURSE_LEVEL_CHOICES, null=True, blank=True)
    prerequisites = models.CharField(max_length=500, null=True, blank=True)

    teacher = models.ForeignKey(UserAccount, related_name='courses')
    credentials = models.CharField(max_length=2000, null=True, blank=True, default='')

    status = models.CharField(max_length=20, choices=COURSE_STATUS_CHOICES, default='UNPUBLISHED')
    created = models.DateTimeField(auto_now_add=True)
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


class CourseVenue(models.Model):
    course = models.OneToOneField(Course)
    venue = models.ForeignKey(Venue, null=True)
    name = models.CharField(max_length=500, null=True, blank=True, default='')
    address = models.CharField(max_length=1000, null=True, blank=True, default='')
    province = models.SmallIntegerField(default=0)
    latlng = models.CharField(max_length=50, null=True, blank=True, default='')


class CourseOutline(models.Model):
    course = models.ForeignKey(Course, related_name='venue')
    title = models.CharField(max_length=500)
    description = models.CharField(max_length=1000, null=True, blank=True, default='')


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


class CourseEnrollment(models.Model):
    code = models.CharField(max_length=20)
    student = models.ForeignKey(UserAccount, related_name='enrollments')
    schedule = models.ForeignKey(CourseSchedule, related_name='enrollments')
    note = models.CharField(max_length=1000, blank=True, default='')

    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=30, choices=COURSE_ENROLLMENT_PAYMENT_STATUS_CHOICES)

    status = models.CharField(max_length=20, choices=COURSE_ENROLLMENT_STATUS_CHOICES)
    status_reason = models.CharField(max_length=100, null=True, blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-schedule__start_datetime']


class CourseReview(models.Model):
    user = models.ForeignKey(UserAccount, related_name='reviews')
    enrollment = models.ForeignKey('CourseEnrollment', related_name='reviews')
    content = models.CharField(max_length=2000)
    is_positive = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)

