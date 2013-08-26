# -*- encoding: utf-8 -*-

import random

from django.conf import settings
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
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

from common.email import send_registration_email
from common.utilities import SHORTUUID_ALPHABETS_NUMBER_ONLY


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
        return Workshop.objects.filter(
            teacher=self
        ).count()

    def stats_courses_teaching(self):
        return Workshop.objects.filter(
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
        return WorkshopFeedback.objects.filter(enrollment__schedule__course__teacher=self).count()

    def stats_feedbacks_given(self):
        return WorkshopFeedback.objects.filter(enrollment__student=self).count()

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