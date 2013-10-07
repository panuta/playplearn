# -*- encoding: utf-8 -*-
from django.conf import settings


class UserRegistrationException(Exception):
    def __init__(self, exception_code, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        self.exception_code = exception_code


class WorkshopScheduleException(Exception):
    def __init__(self, exception_code, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        self.exception_code = exception_code


class WorkshopEnrollmentException(Exception):
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

WORKSHOP_BACKEND_ERRORS = {
    'unauthorized': u'Unauthorized action',

    'edit-while-approving': u'ไม่อนุญาตให้แก้ไขข้อมูลเวิร์คช็อปในขณะกำลังอนุมัติ',
    'submit-before-complete': u'กรุณากรอกข้อมูลเวิร์คช็อปให้ครบถ้วนก่อนส่งอนุมัติ',
    'submit-not-draft': u'เวิร์คช็อปไม่อยู่ในสถานะฉบับร่าง',

    'picture-status-invalid': u'เวิร์คช็อปไม่อยู่ในสถานะที่สามารถแก้ไขได้',
    'picture-notfound': u'ไม่พบไฟล์รูปภาพที่ต้องการแก้ไข',
    'picture-type-invalid': u'ไฟล์ที่อัพโหลดไม่ใช่ไฟล์รูป',
    'picture-numbers-exceed': u'อัพโหลดรูปได้ไม่เกิน %d รูป' % settings.WORKSHOP_MAXIMUM_PICTURE_NUMBER,
    'picture-size-exceed': u'ขนาดของไฟล์รูปไม่เกิน %s เมกะไบต์' % settings.WORKSHOP_MAXIMUM_PICTURE_SIZE_TEXT,

    'place-notfound': u'ไม่พบสถานที่ๆ ต้องการแก้ไข',

    'publish-status-invalid': u'เวิร์คช็อปไม่อยู่ในสถานะที่สามารถเปิดตัวได้',
    'schedule-while-not-published': u'ไม่สามารถเพิ่มรอบได้เพราะเวิร์คช็อปไม่อยู่ในสถานะเปิดตัว',

    'schedule-invalid': u'ข้อมูลที่กรอกไม่อยู่ในรูปแบบที่ถูกต้อง',
    'schedule-duplicated': u'รอบที่ต้องการเพิ่มซ้ำกับรอบที่มีอยู่แล้ว',
    'schedule-past': u'เวลาของรอบที่ต้องการเพิ่มได้ผ่านไปแล้ว',
    'schedule-far': u'ไม่อนุญาตให้เพิ่มรอบที่นานกว่า %d วัน' % settings.WORKSHOP_SCHEDULE_ALLOW_DAYS_IN_ADVANCE,

    'feedback-existed': u'ผู้ใช้เขียนคำนิยมสำหรับรอบนี้ไปแล้ว',
    'feedback-empty': u'กรุณากรอกข้อมูล',
    'feedback-notfound': u'ไม่พบคำนิยมที่ต้องการ',
}

WORKSHOP_RESERVATION_ERRORS = {
    'schedule-notfound': u'ไม่พบรอบที่ต้องการเข้าร่วม',

    'payment-already-confirmed': u'คุณได้แจ้งชำระเงินไปแล้ว',
    'payment-bank-invalid': u'ข้อมูลธนาคารไม่ถูกต้อง',
    'payment-amount-invalid': u'ข้อมูลจำนวนเงินไม่ถูกต้อง',
    'payment-date-invalid': u'ข้อมูลวันที่ไม่ถูกต้อง',
}




WORKSHOP_FEEDBACK_ERRORS = {
    'unauthorized': u'Unauthorized action',
    'existed': u'',
    'empty': u'',
}

WORKSHOP_ENROLLMENT_ERRORS = {
    'workshop-notpublished': u'',
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