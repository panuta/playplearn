# -*- encoding: utf-8 -*-


class UserRegistrationException(Exception):
    def __init__(self, exception_code, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        self.exception_code = exception_code


class CourseEnrollmentException(Exception):
    def __init__(self, exception_code, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        self.exception_code = exception_code


ACCOUNT_REGISTRATION_ERRORS = {
    'email-notfound': u'ไม่ได้กรอกอีเมล',
    'email-invalid': u'อีเมลไม่อยู่ในรูปแบบที่ถูกต้อง',
    'password-notfound': u'ไม่ได้กรอกรหัสผ่าน',
    'user-inactive': u'ผู้ใช้นี้ถูกระงับการใช้งาน',
    'user-invalid': u'อีเมลหรือรหัสผ่านไม่ถูกต้อง',
    'email-registering': u'อีเมลนี้ถูกใช้ลงทะเบียนแล้ว แต่ยังไม่ได้ยืนยันอีเมล',
    'email-registered': u'อีเมลนี้ถูกใช้ลงทะเบียนแล้ว',
}

COURSE_MODIFICATION_ERRORS = {
    'unauthorized': u'Unauthorized action',
    'status-invalid': u'Course status is read only',
    'status-no-ready-to-submit': u'Course is still not ready to be submitted',
    'status-no-ready-to-publish': u'Course is still not ready to be published',
    'input-invalid': u'Input is invalid',
    'course-incomplete': u'Incomplete course details',
    'picture-notfound': u'Picture file is no longer in the system',
    'file-type-invalid': u'File format is invalid',
    'file-number-exceeded': u'Too many files',
    'file-size-exceeded': u'File is too large',
    'place-notfound': u'Place record is not found',
    'schedule-duplicated': u'Duplicated schedule',
    'schedule-past': u'Schedule is already past',
    'schedule-future': u'Schedule is too long',
}

COURSE_FEEDBACK_ERRORS = {
    'unauthorized': u'Unauthorized action',
    'existed': u'',
    'empty': u'',
}

COURSE_ENROLLMENT_ERRORS = {
    'course-notpublished': u'',
    'schedule-notopening': u'',
    'schedule-full': u'',
    'people-invalid': u'',

    'enrollment-notfound': u'',
    'payment-notify-duplicate': u'',
    'payment-notify-input-required': u'',
    'payment-notify-bank-invalid': u'',
    'payment-notify-amount-invalid': u'',
}

MESSAGES_ERRORS = {
    'recipient-notfound': u'Recipient not found',
    'subject-empty': u'Subject is empty',
    'body-empty': u'Message body is empty',
}