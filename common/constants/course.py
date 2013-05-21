
# COURSE STATUS
COURSE_STATUS_CHOICES = (
    ('UNPUBLISHED', 'Unpublished'),
    ('WAIT_FOR_APPROVAL', 'Wait for Approval'),
    ('PUBLISHED', 'Published'),
    ('DELETED', 'Deleted'),
)

COURSE_STATUS_MAP = {
    'UNPUBLISHED': {'name': 'Unpublished'},
    'WAIT_FOR_APPROVAL': {'name': 'Wait for Approval'},
    'PUBLISHED': {'name': 'Published'},
    'DELETED': {'name': 'Deleted'},
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

# COURSE SCHEDULE STATUS
COURSE_SCHEDULE_STATUS_CHOICES = (
    ('PENDING', 'Pending'),
    ('OPENING', 'Opening'),
    ('CANCELLED', 'Cancelled'),
    ('DELETED', 'Deleted'),
)

COURSE_SCHEDULE_STATUS_MAP = {
    'PENDING': {'name': 'Pending'},
    'OPENING': {'name': 'Opening'},
    'CANCELLED': {'name': 'Cancelled'},
    'DELETED': {'name': 'Deleted'},
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