from django.conf.urls import patterns, url

urlpatterns = patterns(
    'messages.views',
    url(r'^inbox/$', 'view_messages_inbox', name='view_messages_inbox'),

    url(r'^ajax/message/send/$', 'ajax_send_message', name='ajax_send_message'),
)