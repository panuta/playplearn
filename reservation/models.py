import decimal

from django.conf import settings
from django.db import models


class Schedule(models.Model):
    STATUS_OPEN = 'O'
    STATUS_CANCELLED = 'C'

    workshop = models.ForeignKey('domain.Workshop')

    start_datetime = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveSmallIntegerField()

    status = models.CharField(max_length=10, default=STATUS_OPEN)
    seats_left = models.PositiveSmallIntegerField()  # calculated

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    # DATA

    def seats_confirmed(self):
        return self.reservations.filter(
            status=Reservation.STATUS_CONFIRMED,
        ).count()

    def seats_confirmed_and_paid(self):
        return self.reservations.filter(
            status=Reservation.STATUS_CONFIRMED,
            payment_status=Reservation.PAYMENT_STATUS_PAID
        ).count()

    def seats_confirmed_and_wait_for_payment(self):
        return self.reservations.filter(
            status=Reservation.STATUS_CONFIRMED,
            payment_status=Reservation.PAYMENT_STATUS_WAIT_FOR_PAYMENT
        ).count()


class Reservation(models.Model):
    STATUS_PENDING = 'P'
    STATUS_CONFIRMED = 'CO'
    STATUS_CANCELLED = 'C'

    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_WAIT_FOR_PAYMENT = 'W'
    PAYMENT_STATUS_PAID = 'PD'
    PAYMENT_STATUS_FAILED = 'F'
    PAYMENT_STATUS_REFUNDED = 'R'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='reservations')
    schedule = models.ForeignKey(Schedule, related_name='reservations')

    price = models.DecimalField(max_digits=10, decimal_places=2)
    seats = models.PositiveSmallIntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)

    code = models.CharField(max_length=20, db_index=True, unique=True)
    status = models.CharField(max_length=20, default=STATUS_PENDING)
    status_reason = models.CharField(max_length=100, blank=True)
    payment_status = models.CharField(max_length=30, default=PAYMENT_STATUS_PENDING)
    note = models.CharField(max_length=1000, blank=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super(Reservation, self).save(*args, **kwargs)

        if not self.pk:
            self.schedule.seats_left -= self.seats
            self.schedule.save()


# USER BALANCE #########################################################################################################

class UserMoneyBalance(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='money_balance')
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=decimal.Decimal('0'))
    date_modified = models.DateTimeField(auto_now=True)


class BalanceTransaction(models.Model):
    RECEIVED_TRANSACTION = 'R'
    PAIDOUT_TRANSACTION = 'P'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='balance_transactions')
    transaction_type = models.CharField(max_length=5)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reservation = models.ForeignKey(Reservation, null=True)
    note = models.CharField(max_length=500, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)




"""
class CourseScheduleManager(models.Manager):
    use_for_related_fields = True

    def get_query_set(self):
        return super(CourseScheduleManager, self).get_query_set().exclude(status='DELETED')


class CourseSchedule(models.Model):
    course = models.ForeignKey(Course, related_name='schedules')
    start_datetime = models.DateTimeField()
    is_opening = models.BooleanField(default=True)
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
"""