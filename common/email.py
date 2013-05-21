from django.conf import settings


def _send_email(from_email, to_emails, subject, text_email_body, html_email_body):
    from django.core.mail import EmailMultiAlternatives
    msg = EmailMultiAlternatives(subject, text_email_body, from_email, to_emails)
    msg.attach_alternative(html_email_body, 'text/html')
    msg.send()


def send_registration_email(to_emails, subject, text_email_body, html_email_body):
    email = settings.EMAIL_MAILBOXES['registration']
    _send_email('%s <%s>' % (email['title'], email['address']), to_emails, subject, text_email_body, html_email_body)


def send_message_email(to_emails, subject, text_email_body, html_email_body):
    email = settings.EMAIL_MAILBOXES['message']
    _send_email('%s <%s>' % (email['title'], email['address']), to_emails, subject, text_email_body, html_email_body)