# -*- encoding: utf-8 -*-

# WORKSHOP STATUS
WORKSHOP_STATUS_CHOICES = (
    ('DRAFT', u'ฉบับร่าง'),
    ('WAIT_FOR_APPROVAL', u'รอการรับรอง'),
    ('READY_TO_PUBLISH', u'พร้อมเปิดตัว'),
    ('PUBLISHED', u'เปิดตัวแล้ว'),
    ('DELETED', u'ถูกลบไปแล้ว'),
)

WORKSHOP_STATUS_MAP = {
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

# WORKSHOP LEVEL
WORKSHOP_LEVEL_CHOICES = (
    ('ANY', 'Any Level'),
    ('BEGINNER', 'Beginner'),
    ('INTERMEDIATE', 'Intermediate'),
    ('ADVANCED', 'Advanced'),
)

WORKSHOP_LEVEL_MAP = {
    'ANY': {'name': 'Any Level'},
    'BEGINNER': {'name': 'Beginner'},
    'INTERMEDIATE': {'name': 'Intermediate'},
    'ADVANCED': {'name': 'Advanced'},
}

# WORKSHOP OUTLINE MEDIA
WORKSHOP_OUTLINE_MEDIA_CHOICES = (
    ('PICTURE', 'Picture'),
    ('VIDEO_URL', 'Video URL'),
    ('VIDEO_UPLOAD', 'Video Upload'),
)

WORKSHOP_OUTLINE_MEDIA_MAP = {
    'PICTURE': {'name': 'Picture'},
    'VIDEO_URL': {'name': 'Video URL'},
    'VIDEO_UPLOAD': {'name': 'Video Upload'},
}

# WORKSHOP SCHEDULE STATUS
WORKSHOP_SCHEDULE_STATUS_CHOICES = (
    ('PENDING', 'Pending'),
    ('OPENING', 'Opening'),
    ('CANCELLED', 'Cancelled'),
)

WORKSHOP_SCHEDULE_STATUS_MAP = {
    'PENDING': {'name': 'Pending'},
    'OPENING': {'name': 'Opening'},
    'CANCELLED': {'name': 'Cancelled'},
}

# WORKSHOP ENROLLMENT STATUS
WORKSHOP_ENROLLMENT_STATUS_CHOICES = (
    ('PENDING', 'Pending'),
    ('CONFIRMED', 'Confirmed'),
    ('CANCELLED', 'Cancelled'),
)

WORKSHOP_ENROLLMENT_STATUS_MAP = {
    'PENDING': {'name': 'Pending'},
    'CONFIRMED': {'name': 'Confirmed'},
    'CANCELLED': {'name': 'Cancelled'},
}

# WORKSHOP ENROLLMENT PAYMENT STATUS
WORKSHOP_ENROLLMENT_PAYMENT_STATUS_CHOICES = (
    ('PENDING', 'Pending'),  # Enrollment record is just created. Payment status is not available.
    ('WAIT_FOR_PAYMENT', 'Wait for Payment'),
    ('PAYMENT_RECEIVED', 'Paid'),
    ('PAYMENT_RECEIVED_FAIL', 'Payment Failed'),
    ('REFUNDED', 'Refunded'),
    ('VOIDED', 'Voided'),
    ('VOIDED_FAIL', 'Voided Failed'),
    ('CANCELLED', 'Cancelled'),
)

WORKSHOP_ENROLLMENT_PAYMENT_STATUS_MAP = {
    'PENDING': {'name': 'Pending'},
    'WAIT_FOR_PAYMENT': {'name': 'Wait for Payment'},
    'PAYMENT_RECEIVED': {'name': 'Paid'},
    'PAYMENT_RECEIVED_FAIL': {'name': 'Payment Failed'},
    'REFUNDED': {'name': 'Refunded'},
    'VOIDED': {'name': 'Voided'},
    'VOIDED_FAIL': {'name': 'Voided Failed'},
    'CANCELLED': {'name': 'Cancelled'},
}

WORKSHOP_ENROLLMENT_PAYMENT_NOTIFY_STATUS_CHOICES = (
    ('RECEIVE', 'Received'),
    ('ACCEPT', 'Accepted'),
    ('REJECT', 'Rejected'),
)

WORKSHOP_ENROLLMENT_PAYMENT_NOTIFY_STATUS_MAP = {
    'RECEIVE': {'name': 'Received'},
    'ACCEPT': {'name': 'Accepted'},
    'REJECT': {'name': 'Rejected'},
}