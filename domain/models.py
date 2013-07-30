# -*- encoding: utf-8 -*-

import decimal
import random
import time

from django.conf import settings
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q, Sum
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.crypto import salted_hmac
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

import shortuuid
from easy_thumbnails.fields import ThumbnailerImageField
from easy_thumbnails.files import get_thumbnailer
from taggit.managers import TaggableManager

from common.constants.course import *
from common.constants.currency import CURRENCY_CHOICES
from common.constants.transaction import TRANSACTION_TYPE_CHOICES
from common.email import send_registration_email
from common.utilities import split_filepath

SHORTUUID_ALPHABETS_NUMBER_ONLY = '1234567890'
SHORTUUID_ALPHABETS_CHARACTERS_NUMBER = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'


# ACCOUNT ##############################################################################################################

class UserAccountManager(BaseUserManager):
    def generate_user_uid(self):
        shortuuid.set_alphabet(SHORTUUID_ALPHABETS_NUMBER_ONLY)
        temp_uuid = shortuuid.uuid()[:10]
        while self.filter(uid=temp_uuid).exists():
            temp_uuid = shortuuid.uuid()[:10]
        return temp_uuid

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
            self.uid = UserAccount.objects.generate_user_uid()

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

    # STATS

    def stats_waiting_for_payment_courses(self):
        return CourseEnrollment.objects.filter(
            student=self, status='PENDING', payment_status='WAIT_FOR_PAYMENT'
        ).count()

    def stats_upcoming_courses(self):
        rightnow = now()

        attending = CourseEnrollment.objects.filter(
            student=self,
            schedule__start_datetime__gt=rightnow,
            status='CONFIRMED').count()

        teaching = CourseSchedule.objects.filter(
            status='OPENING',
            start_datetime__gt=rightnow,
            course__teacher=self).count()

        return attending + teaching

    def stats_total_activities_organizing(self):
        return Course.objects.filter(
            teacher=self
        ).count()

    def stats_courses_teaching(self):
        return Course.objects.filter(
            teacher=self,
            status='PUBLISHED'
        ).count()

    def stats_classes_teaching(self):
        return CourseSchedule.objects.filter(course__teacher=self, course__status='PUBLISHED', status='OPENING').count()

    def stats_students_teaching(self):
        return UserAccount.objects.filter(enrollments__schedule__course__teacher=self, enrollments__status='CONFIRMED', enrollments__schedule__status='OPENING').distinct().count()

    def stats_courses_attended(self):
        # TODO distinct

        rightnow = now()
        return Course.objects.filter(
            schedules__start_datetime__lte=rightnow,
            schedules__enrollments__status='CONFIRMED',
            schedules__enrollments__student=self,
        ).count()

    def stats_courses_attended_and_attending(self):
        # TODO distinct

        return Course.objects.filter(
            schedules__enrollments__status='CONFIRMED',
            schedules__enrollments__student=self,
        ).count()

    def stats_feedbacks_received(self):
        return CourseFeedback.objects.filter(enrollment__schedule__course__teacher=self).count()

    def stats_feedbacks_given(self):
        return CourseFeedback.objects.filter(enrollment__student=self).count()

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
    enrollment = models.ForeignKey('CourseEnrollment', null=True)
    note = models.CharField(max_length=500, blank=True)
    created = models.DateTimeField(auto_now_add=True)


# PLACE ################################################################################################################

class Place(models.Model):
    name = models.CharField(max_length=500, blank=True)
    code = models.CharField(max_length=100, blank=True, db_index=True)
    address = models.CharField(max_length=500, blank=True)
    province_code = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=5, blank=True)
    direction = models.TextField(blank=True)
    latlng = models.CharField(max_length=50, blank=True)

    is_userdefined = models.BooleanField()
    is_visible = models.BooleanField(default=True)  # Only applied to userdefined place
    created_by = models.ForeignKey(UserAccount, null=True)  # Only applied to userdefined place

    class Meta:
        ordering = ['name']

    @property
    def place_url(self):
        if self.code:
            return reverse('view_place_info_by_code', args=(self.code,))
        return reverse('view_place_info_by_id', args=(self.id,))


# COURSE ###############################################################################################################

class CourseSchool(models.Model):
    slug = models.CharField(max_length=300)
    name = models.CharField(max_length=300)
    description = models.CharField(max_length=1000)

    class Meta:
        ordering = ['name']


class CourseManager(models.Manager):
    use_for_related_fields = True

    def get_query_set(self):
        return super(CourseManager, self).get_query_set().exclude(status='DELETED')

    def generate_course_uid(self):
        shortuuid.set_alphabet(SHORTUUID_ALPHABETS_NUMBER_ONLY)
        temp_uuid = shortuuid.uuid()[:10]
        while self.filter(uid=temp_uuid).exists():
            temp_uuid = shortuuid.uuid()[:10]
        return temp_uuid


def course_cover_dir(instance, filename):
    rightnow = now()
    (head, root, ext) = split_filepath(filename)
    return 'users/%s/courses/%s/cover-%d.%s' % (instance.teacher.uid, instance.uid, time.mktime(rightnow.timetuple()), ext)


class Course(models.Model):
    uid = models.CharField(max_length=50, db_index=True, unique=True)
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    schools = models.ManyToManyField(CourseSchool, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_unit = models.CharField(max_length=20, default='THB', choices=CURRENCY_CHOICES)
    duration = models.PositiveSmallIntegerField(null=True, blank=True)
    maximum_people = models.PositiveSmallIntegerField(null=True, blank=True)
    prerequisites = models.CharField(max_length=500, blank=True)

    cover = ThumbnailerImageField(upload_to=course_cover_dir, null=True)
    place = models.ForeignKey(Place, null=True)
    teacher = models.ForeignKey(UserAccount, related_name='courses')

    tags = TaggableManager()
    status = models.CharField(max_length=20, choices=COURSE_STATUS_CHOICES, default='DRAFT')

    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    first_published = models.DateTimeField(null=True)
    last_scheduled = models.DateTimeField(null=True)

    objects = CourseManager()

    class Meta:
        ordering = ['-created']

    def save(self, *args, **kwargs):
        if not self.uid:
            self.uid = Course.objects.generate_course_uid()
        super(Course, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.title

    # PROPERTIES

    def cover_url(self):
        if self.cover:
            return get_thumbnailer(self.cover)['course_cover_normal'].url
        return '%simages/%s' % (settings.STATIC_URL, settings.COURSE_COVER_DEFAULT_NORMAL)

    def small_cover_url(self):
        if self.cover:
            return get_thumbnailer(self.cover)['course_cover_small'].url
        return '%simages/%s' % (settings.STATIC_URL, settings.COURSE_COVER_DEFAULT_SMALL)

    def get_school(self):
        if self.schools:
            return self.schools.all()[0]
        return None

    def status_info(self):
        return COURSE_STATUS_MAP[str(self.status)]

    def status_name(self):
        return COURSE_STATUS_MAP[str(self.status)]['name']

    # DATA

    def get_upcoming_schedule(self):
        rightnow = now()
        schedules = CourseSchedule.objects.filter(course=self, status='OPENING', start_datetime__gte=rightnow).order_by('start_datetime')
        return schedules[0] if schedules else None

    def get_last_schedule(self):
        rightnow = now()
        return CourseSchedule.objects.filter(course=self, status='OPENING', start_datetime__lt=rightnow).order_by('-start_datetime')[0]

    def get_promoted_feedbacks(self):
        return CourseFeedback.objects.filter(enrollment__schedule__course=self, is_promoted=True).order_by('-created')

    # PERMISSIONS

    def can_view(self, user):
        return (self.status == 'PUBLISHED') or (self.status == 'UNPUBLISHED' and user == self.teacher) or \
               (self.status == 'WAIT_FOR_APPROVAL' and (user == self.teacher or user.is_staff()))

    # STATS

    def stats_upcoming_classes(self):
        rightnow = now()
        return CourseSchedule.objects.filter(course=self, status='OPENING', start_datetime__gte=rightnow).count()

    def stats_opening_classes(self):
        return CourseSchedule.objects.filter(course=self, status='OPENING').count()

    def stats_students(self):
        return UserAccount.objects.filter(
            enrollments__schedule__course=self,
            enrollments__status='CONFIRMED',
            enrollments__payment_status='PAYMENT_RECEIVED',
            enrollments__schedule__status='OPENING'
        ).distinct().count()

    def stats_feedbacks(self):
        return CourseFeedback.objects.filter(enrollment__schedule__course=self).count()

    def stats_total_earning(self):
        total_earning = CourseEnrollment.objects.filter(schedule__course=self, status='CONFIRMED', payment_status='PAYMENT_RECEIVED').aggregate(Sum('total'))['total__sum']
        return total_earning if total_earning else 0


def editing_course_cover_dir(instance, filename):
    rightnow = now()
    (head, root, ext) = split_filepath(filename)
    return 'users/%s/courses/%s/cover-%d.%s' % (instance.course.teacher.uid, instance.course.uid, time.mktime(rightnow.timetuple()), ext)


class EditingCourse(models.Model):
    course = models.OneToOneField(Course, related_name='editing_course')
    cover = ThumbnailerImageField(upload_to=editing_course_cover_dir, null=True)


# Course Activities

class CourseActivity(models.Model):
    course = models.ForeignKey(Course, related_name='activities')
    title = models.CharField(max_length=500)
    description = models.CharField(max_length=1000, blank=True)
    ordering = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['ordering']


# Course Pictures

def course_picture_dir(instance, filename):
    (head, root, ext) = split_filepath(filename)
    return 'users/%s/courses/%s/%s.%s' % (instance.course.teacher.uid, instance.course.uid, instance.uid, ext)


class CoursePictureManager(models.Manager):
    def generate_media_uid(self):
        shortuuid.set_alphabet(SHORTUUID_ALPHABETS_CHARACTERS_NUMBER)
        temp_uuid = shortuuid.uuid()[0:10]
        while CoursePicture.objects.filter(uid=temp_uuid).exists():
            temp_uuid = shortuuid.uuid()[0:10]
        return temp_uuid


class CoursePicture(models.Model):
    course = models.ForeignKey(Course, related_name='pictures')
    uid = models.CharField(max_length=50, db_index=True, unique=True)
    description = models.CharField(max_length=1000, blank=True)
    image = ThumbnailerImageField(upload_to=course_picture_dir)
    ordering = models.PositiveSmallIntegerField(default=0)
    uploaded = models.DateTimeField(auto_now_add=True)
    is_visible = models.BooleanField(default=False)

    mark_added = models.BooleanField(default=False)
    mark_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['ordering']

    objects = CoursePictureManager()

    def save(self, *args, **kwargs):
        if not self.uid:
            self.uid = self.__class__.objects.generate_media_uid()
        super(CoursePicture, self).save(*args, **kwargs)


# Course Schedule

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

    # STATS

    def stats_seats_reserved(self):
        return CourseEnrollment.objects.filter(schedule=self, status='CONFIRMED').count()

    def stats_seats_left(self):
        return self.course.maximum_people - self.stats_seats_reserved()


# Course Enrollment

class CourseEnrollmentManager(models.Manager):
    def generate_enrollment_code(self):
        shortuuid.set_alphabet(SHORTUUID_ALPHABETS_NUMBER_ONLY)
        temp_uuid = shortuuid.uuid()[0:10]
        while CourseEnrollment.objects.filter(code=temp_uuid).exists() or \
                UnauthenticatedCourseEnrollment.objects.filter(code=temp_uuid).exists():
            temp_uuid = shortuuid.uuid()[0:10]
        return temp_uuid

    def create_enrollment_from_unauthenticated(self, user, unauthenticated_enrollment):
        return CourseEnrollment.objects.create(
            student=user,
            schedule=unauthenticated_enrollment.schedule,
            price=unauthenticated_enrollment.price,
            total=unauthenticated_enrollment.price,
            status='PENDING',
            payment_status='WAIT_FOR_PAYMENT',
        )


class BaseCourseEnrollment(models.Model):
    code = models.CharField(max_length=20, db_index=True, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    people = models.PositiveSmallIntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.CharField(max_length=1000, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    objects = CourseEnrollmentManager()

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.__class__.objects.generate_enrollment_code()
        super(BaseCourseEnrollment, self).save(*args, **kwargs)


class CourseEnrollment(BaseCourseEnrollment):
    student = models.ForeignKey(UserAccount, related_name='enrollments')
    schedule = models.ForeignKey(CourseSchedule, related_name='enrollments')
    is_public = models.BooleanField(default=False)
    payment_status = models.CharField(max_length=30, choices=COURSE_ENROLLMENT_PAYMENT_STATUS_CHOICES)
    status = models.CharField(max_length=20, choices=COURSE_ENROLLMENT_STATUS_CHOICES)
    status_reason = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-schedule__start_datetime']

    def has_feedback(self):
        return CourseFeedback.objects.filter(enrollment=self).exists()

    def is_payment_notified(self):
        return CourseEnrollmentPaymentNotify.objects.filter(enrollment=self, status='RECEIVE').exists()


class UnauthenticatedCourseEnrollment(BaseCourseEnrollment):
    key = models.CharField(max_length=100, db_index=True, unique=True)
    schedule = models.ForeignKey(CourseSchedule, related_name='unauthenticated_enrollments')


class CourseEnrollmentPaymentNotify(models.Model):
    enrollment = models.ForeignKey(CourseEnrollment)
    bank = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transfered_on = models.DateTimeField()
    notified_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, default='RECEIVE', choices=COURSE_ENROLLMENT_PAYMENT_NOTIFY_STATUS_CHOICES)
    remark = models.CharField(max_length=500)


# COURSE FEEDBACK ######################################################################################################

class CourseFeedback(models.Model):
    enrollment = models.OneToOneField('CourseEnrollment', related_name='feedback')
    content = models.CharField(max_length=2000, blank=True)
    feelings = models.CharField(max_length=500, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=False)
    is_promoted = models.BooleanField(default=False)
