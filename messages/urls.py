from django.conf.urls import patterns, url

OPTION_MESSAGES = 'm'
OPTIONS = OPTION_MESSAGES

urlpatterns = patterns(
    'messages.views',

    url(r'^inbox/(?:(?P<option>'+OPTIONS+')/)?$', 'view_messages_inbox', name='postman_inbox'),
    url(r'^sent/(?:(?P<option>'+OPTIONS+')/)?$', 'view_messages_sent', name='postman_sent'),
    url(r'^trash/(?:(?P<option>'+OPTIONS+')/)?$', 'view_messages_trash', name='postman_trash'),

    url(r'^reply/(?P<message_id>[\d]+)/$', 'reply_message', name='postman_reply'),

    url(r'^thread/(?P<message_id>[\d]+)/$', 'view_message', name='view_message'),

    url(r'^ajax/message/send/$', 'ajax_send_message', name='ajax_send_message'),
)