from django.conf.urls import patterns, url

urlpatterns = patterns(
    'presentation.views.views',
    url(r'^$', 'view_homepage', name='view_homepage'),
    url(r'^about_us/$', 'view_about_us_page', name='view_about_us_page'),
    url(r'^faq/$', 'view_faq_page', name='view_faq_page'),
    url(r'^policy/$', 'view_policy_page', name='view_policy_page'),

    url(r'^place/id/(?P<place_id>\d+)/$', 'view_place_info_by_id', name='view_place_info_by_id'),
    url(r'^place/(?P<place_code>\w+)/$', 'view_place_info_by_code', name='view_place_info_by_code'),
)

urlpatterns += patterns(
    'presentation.views.workshop_views',

    url(r'^workshop/(?P<workshop_uid>\w+)/$', 'view_workshop_outline', {'page_action': '', 'reservation_code': ''}, name='view_workshop_outline'),
    url(r'^workshop/(?P<workshop_uid>\w+)/payment/(?P<reservation_code>\d+)/$', 'view_workshop_outline', {'page_action': 'payment'}, name='view_workshop_outline_with_payment'),

    url(r'^ajax/activity/enroll/$', 'enroll_workshop', name='enroll_workshop'),
    url(r'^ajax/activity/enroll/login/(?P<backend>[^/]+)/$', 'login_to_enroll_workshop', name='login_to_enroll_workshop'),

    url(r'^activities/$', 'view_workshops_browse', {'browse_by': ''}, name='view_workshops_browse'),
    url(r'^activities/topic/(?P<topic_slug>\w+)/$', 'view_workshops_browse_by_topic', name='view_workshops_browse_by_topic'),
    url(r'^activities/(?P<browse_by>\w+)/$', 'view_workshops_browse', name='view_workshops_browse_by_category'),

    url(r'^teach/$', 'view_workshop_teach', name='view_workshop_teach'),

    url(r'^ajax/workshop/topics/search/$', 'search_workshop_topics', name='search_workshop_topics'),
)

"""
urlpatterns += patterns(
    'presentation.views.classroom_views',

    url(r'^classroom/(?P<workshop_uid>\w+)/$', 'view_classroom_home', name='view_classroom_home'),
    url(r'^classroom/(?P<workshop_uid>\w+)/conversation/$', 'view_classroom_conversation', name='view_classroom_conversation'),
    url(r'^classroom/(?P<workshop_uid>\w+)/qa/$', 'view_classroom_qa', name='view_classroom_qa'),
    url(r'^classroom/(?P<workshop_uid>\w+)/announcement/$', 'view_classroom_announcement', name='view_classroom_announcement'),
)
"""

urlpatterns += patterns(
    'presentation.views.workshop_backend_views',
    #url(r'^my/activities/payment/$', 'view_my_workshops_payment', name='view_my_workshops_payment'),
    #url(r'^my/activities/upcoming/$', 'view_my_workshops_upcoming', name='view_my_workshops_upcoming'),

    url(r'^my/workshops/attend/$', 'view_my_workshops_attend', name='view_my_workshops_attend'),

    #url(r'^my/activities/attended/(?P<school_slug>\w+)/$', 'view_my_workshops_attended_in_school', name='view_my_workshops_attended_in_school'),
    url(r'^my/workshops/organize/$', 'view_my_workshops_organize', name='view_my_workshops_organize'),

    url(r'^my/workshop/new/$', 'create_workshop', name='create_workshop'),
    url(r'^workshop/(?P<workshop_uid>\w+)/edit/$', 'edit_workshop', name='edit_workshop'),
    url(r'^workshop/(?P<workshop_uid>\w+)/revert/$', 'revert_approving_workshop', name='revert_approving_workshop'),

    url(r'^workshop/(?P<workshop_uid>\w+)/manage/overview/$', 'manage_workshop_overview', name='manage_workshop_overview'),
    url(r'^workshop/(?P<workshop_uid>\w+)/manage/schedule/$', 'manage_workshop_schedule', {'date_string': '', 'time_string': ''}, name='manage_workshop_schedule'),
    url(r'^workshop/(?P<workshop_uid>\w+)/manage/schedule/(?P<date_string>\w+)/$', 'manage_workshop_schedule', {'time_string': ''}, name='manage_workshop_schedule_date'),
    url(r'^workshop/(?P<workshop_uid>\w+)/manage/schedule/(?P<date_string>\w+)/(?P<time_string>\w+)/$', 'manage_workshop_schedule', name='manage_workshop_schedule_datetime'),
    url(r'^workshop/(?P<workshop_uid>\w+)/manage/feedbacks/$', 'manage_workshop_feedbacks', name='manage_workshop_feedbacks'),

    url(r'^enrollment/(?P<enrollment_code>\d+)/$', 'view_enrollment_details', {'with_payment': False}, name='view_enrollment_details'),
    url(r'^enrollment/(?P<enrollment_code>\d+)/payment/$', 'view_enrollment_details', {'with_payment': True}, name='view_enrollment_details_with_payment'),
)

urlpatterns += patterns(
    'presentation.views.workshop_backend_ajax_views',

    url(r'^ajax/workshop/save/$', 'ajax_save_workshop', name='ajax_save_workshop'),
    url(r'^ajax/workshop/picture/upload/$', 'ajax_upload_workshop_picture', name='ajax_upload_workshop_picture'),
    url(r'^ajax/workshop/picture/delete/$', 'ajax_delete_workshop_picture', name='ajax_delete_workshop_picture'),
    url(r'^ajax/workshop/place/get/$', 'ajax_get_workshop_place', name='ajax_get_workshop_place'),

    url(r'^ajax/workshop/publish/$', 'ajax_publish_workshop', name='ajax_publish_workshop'),

    url(r'^ajax/workshop/schedule/add/$', 'ajax_add_workshop_schedule', name='ajax_add_workshop_schedule'),

    url(r'^ajax/workshop/feedback/view/$', 'ajax_view_workshop_feedback', name='ajax_view_workshop_feedback'),
    url(r'^ajax/workshop/feedback/add/$', 'ajax_add_workshop_feedback', name='ajax_add_workshop_feedback'),
    url(r'^ajax/workshop/feedback/delete/$', 'ajax_delete_workshop_feedback', name='ajax_delete_workshop_feedback'),
    url(r'^ajax/workshop/feedback/visibility/$', 'ajax_set_workshop_feedback_visibility', name='ajax_set_workshop_feedback_visibility'),

    url(r'^ajax/enrollment/details/$', 'ajax_view_enrollment_details', name='ajax_view_enrollment_details'),
    url(r'^ajax/enrollment/payment/notify/$', 'ajax_notify_enrollment_payment', name='ajax_notify_enrollment_payment'),
)

urlpatterns += patterns(
    'presentation.views.user_views',
    url(r'^my/profile/$', 'view_my_profile', name='view_my_profile'),
    url(r'^profile/(?P<user_uid>\w+)/$', 'view_user_profile', name='view_user_profile'),

    url(r'^settings/profile/$', 'edit_my_settings_profile', name='edit_my_settings_profile'),
    url(r'^settings/social/$', 'edit_my_settings_social', name='edit_my_settings_social'),
    url(r'^settings/notifications/$', 'edit_my_settings_notifications', name='edit_my_settings_notifications'),
    url(r'^settings/account/$', 'edit_my_settings_account_email', name='edit_my_settings_account_email'),
    url(r'^settings/account/password/$', 'edit_my_settings_account_password', name='edit_my_settings_account_password'),

    url(r'^news_feed/$', 'view_my_news_feed', name='view_my_news_feed'),
)
