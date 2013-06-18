from django.conf import settings
from django.conf.urls import patterns, url
from django.views.generic import TemplateView

urlpatterns = patterns(
    'accounts.views',
    url(r'^login/$', 'view_user_login', {'action':'login'}, name='view_user_login'),
    url(r'^login/signup/$', 'view_user_login', {'action':'signup'}, name='view_user_login_signup'),
    url(r'^login/resend/$', 'view_user_login', {'action':'resend'}, name='view_user_login_resend'),

    url(r'^login/facebook/$', 'login_facebook', name='login_facebook'),
    url(r'^accounts/error/$', TemplateView.as_view(template_name="account/registration/registration_login_error.html"), name='view_user_login_error'),
    url(r'^signup/done/$', 'view_user_signup_done', name='view_user_signup_done'),
    url(r'^activate/(?P<key>\w+)/$', 'activate_email_user', name='activate_email_user'),
    url(r'^accounts/redirect/$', 'login_facebook_redirect', name='login_facebook_redirect'),

    url(r'^ajax/email/login/$', 'ajax_email_login', name='ajax_email_login'),
    url(r'^ajax/email/register/$', 'ajax_email_register', name='ajax_email_register'),
)

urlpatterns += patterns(
    '',
    url(r'^account/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='auth_logout'),
    url(r'^account/password_reset/$', 'django.contrib.auth.views.password_reset',
        {'from_email': settings.EMAIL_MAILBOXES['registration']['address']}, name='auth_password_reset'),
    url(r'^account/password_reset/done/$', 'django.contrib.auth.views.password_reset_done',
        name='auth_password_reset_done'),
    url(r'^account/reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'django.contrib.auth.views.password_reset_confirm', name='auth_password_reset_confirm'),
    url(r'^account/reset/done/$', 'django.contrib.auth.views.password_reset_complete',
        name='auth_password_reset_complete'),
)