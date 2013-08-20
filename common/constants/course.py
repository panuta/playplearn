# -*- encoding: utf-8 -*-

# COURSE STATUS
COURSE_STATUS_CHOICES = (
    ('DRAFT', u'ฉบับร่าง'),
    ('WAIT_FOR_APPROVAL', u'รอการรับรอง'),
    ('READY_TO_PUBLISH', u'พร้อมเปิดตัว'),
    ('PUBLISHED', u'เปิดตัวแล้ว'),
    ('DELETED', u'ถูกลบไปแล้ว'),
)

COURSE_STATUS_MAP = {
    'DRAFT': {
        'name': u'ฉบับร่าง',
        'css_class': 'draft',
    },
    'WAIT_FOR_APPROVAL': {
        'name': u'รอการรับรอง',
        'css_class': 'wait_for_approval',
    },
    'READY_TO_PUBLISH': {
        'name': u'พร้อมเปิดตัว',
        'css_class': 'ready_to_publish',
    },
    'PUBLISHED': {
        'name': u'เปิดตัวแล้ว',
        'css_class': 'published',
    },
    'DELETED': {
        'name': u'ถูกลบไปแล้ว',
        'css_class': 'deleted',
    },
}

# COURSE LEVEL
COURSE_LEVEL_CHOICES = (
    ('ANY', 'Any Level'),
    ('BEGINNER', 'Beginner'),
    ('INTERMEDIATE', 'Intermediate'),
    ('ADVANCED', 'Advanced'),
)

COURSE_LEVEL_MAP = {
    'ANY': {'name': 'Any Level'},
    'BEGINNER': {'name': 'Beginner'},
    'INTERMEDIATE': {'name': 'Intermediate'},
    'ADVANCED': {'name': 'Advanced'},
}

# COURSE OUTLINE MEDIA
COURSE_OUTLINE_MEDIA_CHOICES = (
    ('PICTURE', 'Picture'),
    ('VIDEO_URL', 'Video URL'),
    ('VIDEO_UPLOAD', 'Video Upload'),
)

COURSE_OUTLINE_MEDIA_MAP = {
    'PICTURE': {'name': 'Picture'},
    'VIDEO_URL': {'name': 'Video URL'},
    'VIDEO_UPLOAD': {'name': 'Video Upload'},
}

# COURSE SCHEDULE STATUS
COURSE_SCHEDULE_STATUS_CHOICES = (
    ('PENDING', 'Pending'),
    ('OPENING', 'Opening'),
    ('CANCELLED', 'Cancelled'),
)

COURSE_SCHEDULE_STATUS_MAP = {
    'PENDING': {'name': 'Pending'},
    'OPENING': {'name': 'Opening'},
    'CANCELLED': {'name': 'Cancelled'},
}

# COURSE ENROLLMENT STATUS
COURSE_ENROLLMENT_STATUS_CHOICES = (
    ('PENDING', 'Pending'),
    ('CONFIRMED', 'Confirmed'),
    ('CANCELLED', 'Cancelled'),
)

COURSE_ENROLLMENT_STATUS_MAP = {
    'PENDING': {'name': 'Pending'},
    'CONFIRMED': {'name': 'Confirmed'},
    'CANCELLED': {'name': 'Cancelled'},
}

# COURSE ENROLLMENT PAYMENT STATUS
COURSE_ENROLLMENT_PAYMENT_STATUS_CHOICES = (
    ('PENDING', 'Pending'),  # Enrollment record is just created. Payment status is not available.
    ('WAIT_FOR_PAYMENT', 'Wait for Payment'),
    ('PAYMENT_RECEIVED', 'Paid'),
    ('PAYMENT_RECEIVED_FAIL', 'Payment Failed'),
    ('REFUNDED', 'Refunded'),
    ('VOIDED', 'Voided'),
    ('VOIDED_FAIL', 'Voided Failed'),
    ('CANCELLED', 'Cancelled'),
)

COURSE_ENROLLMENT_PAYMENT_STATUS_MAP = {
    'PENDING': {'name': 'Pending'},
    'WAIT_FOR_PAYMENT': {'name': 'Wait for Payment'},
    'PAYMENT_RECEIVED': {'name': 'Paid'},
    'PAYMENT_RECEIVED_FAIL': {'name': 'Payment Failed'},
    'REFUNDED': {'name': 'Refunded'},
    'VOIDED': {'name': 'Voided'},
    'VOIDED_FAIL': {'name': 'Voided Failed'},
    'CANCELLED': {'name': 'Cancelled'},
}

COURSE_ENROLLMENT_PAYMENT_NOTIFY_STATUS_CHOICES = (
    ('RECEIVE', 'Received'),
    ('ACCEPT', 'Accepted'),
    ('REJECT', 'Rejected'),
)

COURSE_ENROLLMENT_PAYMENT_NOTIFY_STATUS_MAP = {
    'RECEIVE': {'name': 'Received'},
    'ACCEPT': {'name': 'Accepted'},
    'REJECT': {'name': 'Rejected'},
}