# -*- encoding: utf-8 -*-

import random
import time

from django.conf import settings
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Sum
from django.template.loader import render_to_string
from django.utils.crypto import salted_hmac
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

import shortuuid
from easy_thumbnails.fields import ThumbnailerImageField
from easy_thumbnails.files import get_thumbnailer
from taggit.managers import TaggableManager

from common.constants.workshop import *
from common.email import send_registration_email
from common.utilities import split_filepath, SHORTUUID_ALPHABETS_NUMBER_ONLY, SHORTUUID_ALPHABETS_CHARACTERS_NUMBER

from reservation.models import Reservation, Schedule, BalanceTransaction, UserMoneyBalance


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

        super(UserAccount, self).save(*args, **kwargs)
        UserMoneyBalance.objects.get_or_create(user=self)

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
        rightnow = timezone.now()

        attending = CourseEnrollment.objects.filter(
            student=self,
            schedule__start_datetime__gt=rightnow,
            status='CONFIRMED').count()

        teaching = CourseSchedule.objects.filter(
            status='OPENING',
            start_datetime__gt=rightnow,
            course__teacher=self).count()

        return attending + teaching

    def stats_workshops_organizing(self):
        return Workshop.objects.filter(
            teacher=self,
            status=Workshop.STATUS_PUBLISHED
        ).count()

    def stats_courses_attended(self):
        # TODO distinct

        rightnow = timezone.now()
        return Workshop.objects.filter(
            schedules__start_datetime__lte=rightnow,
            schedules__enrollments__status='CONFIRMED',
            schedules__enrollments__student=self,
            ).count()

    def stats_courses_attended_and_attending(self):
        # TODO distinct

        return Workshop.objects.filter(
            schedules__enrollments__status='CONFIRMED',
            schedules__enrollments__student=self,
            ).count()

    def stats_feedbacks_received(self):
        return WorkshopFeedback.objects.filter(reservation__schedule__workshop__teacher=self).count()

    def stats_feedbacks_given(self):
        return WorkshopFeedback.objects.filter(reservation__student=self).count()

    def stats_total_earning(self):
        total_earning = BalanceTransaction.objects.filter(transaction_type=BalanceTransaction.RECEIVED_TRANSACTION).aggregate(Sum('amount'))['amount__sum']
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


# WORKSHOP #############################################################################################################

class WorkshopTopic(models.Model):
    slug = models.CharField(max_length=300)
    name = models.CharField(max_length=300)
    description = models.CharField(max_length=1000)

    class Meta:
        ordering = ['name']


class WorkshopManager(models.Manager):
    use_for_related_fields = True

    def get_query_set(self):
        return super(WorkshopManager, self).get_query_set().exclude(status='DELETED')

    def generate_workshop_uid(self):
        shortuuid.set_alphabet(SHORTUUID_ALPHABETS_NUMBER_ONLY)
        temp_uuid = shortuuid.uuid()[:10]
        while self.filter(uid=temp_uuid).exists():
            temp_uuid = shortuuid.uuid()[:10]
        return temp_uuid


class Workshop(models.Model):
    STATUS_DRAFT = 'D'
    STATUS_WAIT_FOR_APPROVAL = 'W'
    STATUS_READY_TO_PUBLISH = 'R'
    STATUS_PUBLISHED = 'P'

    uid = models.CharField(max_length=50, db_index=True, unique=True)
    title = models.CharField(max_length=500)
    short_description = models.CharField(max_length=1000)
    description = models.TextField(blank=True)
    topics = models.ManyToManyField(WorkshopTopic, null=True)
    duration = models.PositiveSmallIntegerField(null=True, blank=True)
    prerequisites = models.CharField(max_length=500, blank=True)
    place = models.ForeignKey(Place, null=True, related_name='workshops')
    teacher = models.ForeignKey(UserAccount, related_name='workshops')

    default_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    default_capacity = models.PositiveSmallIntegerField(null=True, blank=True)

    tags = TaggableManager()
    status = models.CharField(max_length=20, default=STATUS_DRAFT)

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    date_published = models.DateTimeField(null=True)

    objects = WorkshopManager()

    class Meta:
        ordering = ['-date_created']

    def save(self, *args, **kwargs):
        if not self.uid:
            self.uid = Workshop.objects.generate_workshop_uid()
        super(Workshop, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.title

    # STATUS

    def is_status_draft(self):
        return self.status == Workshop.STATUS_DRAFT

    def is_status_wait_for_approval(self):
        return self.status == Workshop.STATUS_WAIT_FOR_APPROVAL

    def is_status_ready_to_publish(self):
        return self.status == Workshop.STATUS_READY_TO_PUBLISH

    def is_status_published(self):
        return self.status == Workshop.STATUS_PUBLISHED

    # PROPERTIES

    def get_school(self):
        if self.schools:
            return self.schools.all()[0]
        return None

    def status_info(self):
        return WORKSHOP_STATUS_MAP[str(self.status)]

    def status_name(self):
        return WORKSHOP_STATUS_MAP[str(self.status)]['name']

    def cover_picture(self):
        pictures = WorkshopPicture.objects.filter(workshop=self, is_visible=True).order_by('ordering')
        return pictures[0] if pictures else None

    # DATA

    def is_outline_completed(self):
        from .functions import is_workshop_outline_completed
        return is_workshop_outline_completed(self)

    def get_upcoming_schedule(self):
        rightnow = timezone.now()
        schedules = Schedule.objects.filter(workshop=self, status=Schedule.STATUS_OPEN, start_datetime__gte=rightnow).order_by('start_datetime')
        return schedules[0] if schedules else None

    def get_available_upcoming_schedule(self):
        rightnow = timezone.now()
        schedules = Schedule.objects.filter(workshop=self, seats_left__gt=0, status=Schedule.STATUS_OPEN, start_datetime__gte=rightnow).order_by('start_datetime')
        return schedules[0] if schedules else None

    def get_last_schedule(self):
        rightnow = timezone.now()
        return WorkshopSchedule.objects.filter(workshop=self, status='OPENING', start_datetime__lt=rightnow).order_by('-start_datetime')[0]

    def get_promoted_feedbacks(self):
        return WorkshopFeedback.objects.filter(enrollment__schedule__workshop=self, is_promoted=True).order_by('-created')

    # PERMISSIONS

    def can_view(self, user):
        return (self.status == Workshop.STATUS_PUBLISHED) or (self.status == Workshop.STATUS_DRAFT and user == self.teacher) or \
               (self.status == Workshop.STATUS_WAIT_FOR_APPROVAL and (user == self.teacher or user.is_staff()))

    # STATS

    def stats_upcoming_schedules(self):
        rightnow = timezone.now()
        return Schedule.objects.filter(workshop=self, status=Schedule.STATUS_OPEN, start_datetime__gte=rightnow).count()

    def stats_opening_schedules(self):
        return Schedule.objects.filter(workshop=self, status=Schedule.STATUS_OPEN).count()

    def stats_students(self):
        return UserAccount.objects.filter(
            reservations__schedule__workshop=self,
            reservations__status=Reservation.STATUS_CONFIRMED,
            reservations__payment_status=Reservation.PAYMENT_STATUS_PAID,
        ).distinct().count()

    def stats_feedbacks(self):
        return WorkshopFeedback.objects.filter(reservation__schedule__workshop=self).count()

    def stats_total_earned(self):
        total_earning = Reservation.objects.filter(schedule__workshop=self, status=Reservation.STATUS_CONFIRMED, payment_status=Reservation.PAYMENT_STATUS_PAID).aggregate(Sum('total'))['total__sum']
        return total_earning if total_earning else 0


class WorkshopActivity(models.Model):
    workshop = models.ForeignKey(Workshop, related_name='activities')
    title = models.CharField(max_length=500)
    description = models.CharField(max_length=1000, blank=True)
    ordering = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['ordering']


def workshop_picture_dir(instance, filename):
    (head, root, ext) = split_filepath(filename)
    return 'users/%s/workshops/%s/%s.%s' % (instance.workshop.teacher.uid, instance.workshop.uid, instance.uid, ext)


class WorkshopPictureManager(models.Manager):
    def generate_media_uid(self):
        shortuuid.set_alphabet(SHORTUUID_ALPHABETS_CHARACTERS_NUMBER)
        temp_uuid = shortuuid.uuid()[0:10]
        while WorkshopPicture.objects.filter(uid=temp_uuid).exists():
            temp_uuid = shortuuid.uuid()[0:10]
        return temp_uuid


class WorkshopPicture(models.Model):
    workshop = models.ForeignKey(Workshop, related_name='pictures')
    uid = models.CharField(max_length=50, db_index=True, unique=True)
    description = models.CharField(max_length=1000, blank=True)
    image = ThumbnailerImageField(upload_to=workshop_picture_dir)
    ordering = models.PositiveSmallIntegerField(default=0)
    uploaded = models.DateTimeField(auto_now_add=True)
    is_visible = models.BooleanField(default=False)

    mark_added = models.BooleanField(default=False)
    mark_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['ordering']

    objects = WorkshopPictureManager()

    def save(self, *args, **kwargs):
        if not self.uid:
            self.uid = self.__class__.objects.generate_media_uid()
        super(WorkshopPicture, self).save(*args, **kwargs)


# WORKSHOP FEEDBACK ####################################################################################################

class WorkshopFeedback(models.Model):
    reservation = models.OneToOneField(Reservation, related_name='feedback')
    content = models.CharField(max_length=2000, blank=True)
    feelings = models.CharField(max_length=500, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=False)
    is_promoted = models.BooleanField(default=False)
