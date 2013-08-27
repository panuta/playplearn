# -*- encoding: utf-8 -*-

import time

from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q, Sum
from django.utils.timezone import now

import shortuuid
from easy_thumbnails.fields import ThumbnailerImageField
from taggit.managers import TaggableManager

from common.constants.workshop import *
from common.utilities import split_filepath, SHORTUUID_ALPHABETS_NUMBER_ONLY, SHORTUUID_ALPHABETS_CHARACTERS_NUMBER

from account.models import UserAccount
from reservation.models import Reservation, Schedule


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


def workshop_cover_dir(instance, filename):
    rightnow = now()
    (head, root, ext) = split_filepath(filename)
    return 'users/%s/workshops/%s/cover-%d.%s' % (instance.teacher.uid, instance.uid, time.mktime(rightnow.timetuple()), ext)


class Workshop(models.Model):
    STATUS_DRAFT = 'D'
    STATUS_WAIT_FOR_APPROVAL = 'W'
    STATUS_READY_TO_PUBLISH = 'R'
    STATUS_PUBLISHED = 'P'

    uid = models.CharField(max_length=50, db_index=True, unique=True)
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    topics = models.ManyToManyField(WorkshopTopic, null=True)
    duration = models.PositiveSmallIntegerField(null=True, blank=True)
    prerequisites = models.CharField(max_length=500, blank=True)
    place = models.ForeignKey(Place, null=True)
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

    # DATA

    def get_upcoming_schedule(self):
        rightnow = now()

        schedules = Schedule.objects.filter(workshop=self, status=Schedule.STATUS_OPEN, start_datetime__gte=rightnow).order_by('start_datetime')
        return schedules[0] if schedules else None

    def get_available_upcoming_schedule(self):
        rightnow = now()
        schedules = Schedule.objects.filter(workshop=self, seats_left__gt=0, status=Schedule.STATUS_OPEN, start_datetime__gte=rightnow).order_by('start_datetime')
        return schedules[0] if schedules else None

    def get_last_schedule(self):
        rightnow = now()
        return WorkshopSchedule.objects.filter(workshop=self, status='OPENING', start_datetime__lt=rightnow).order_by('-start_datetime')[0]

    def get_promoted_feedbacks(self):
        return WorkshopFeedback.objects.filter(enrollment__schedule__workshop=self, is_promoted=True).order_by('-created')

    # PERMISSIONS

    def can_view(self, user):
        return (self.status == Workshop.STATUS_PUBLISHED) or (self.status == Workshop.STATUS_DRAFT and user == self.teacher) or \
               (self.status == Workshop.STATUS_WAIT_FOR_APPROVAL and (user == self.teacher or user.is_staff()))

    # STATS

    def stats_upcoming_classes(self):
        rightnow = now()
        return Schedule.objects.filter(workshop=self, status=Schedule.STATUS_OPEN, start_datetime__gte=rightnow).count()

    def stats_opening_classes(self):  # TODO Rename to all classes
        return Schedule.objects.filter(workshop=self, status=Schedule.STATUS_OPEN).count()

    def stats_students(self):
        return UserAccount.objects.filter(
            enrollments__schedule__workshop=self,
            enrollments__status='CONFIRMED',
            enrollments__payment_status='PAYMENT_RECEIVED',
            enrollments__schedule__status='OPENING'
        ).distinct().count()

    def stats_feedbacks(self):
        return WorkshopFeedback.objects.filter(reservation__schedule__workshop=self).count()

    def stats_total_earning(self):
        total_earning = WorkshopEnrollment.objects.filter(schedule__workshop=self, status='CONFIRMED', payment_status='PAYMENT_RECEIVED').aggregate(Sum('total'))['total__sum']
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
