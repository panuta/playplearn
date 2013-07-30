from django.conf.urls import patterns, url

urlpatterns = patterns(
    'presentation.views.views',
    url(r'^$', 'view_homepage', name='view_homepage'),
    url(r'^faq/$', 'view_faq_page', name='view_faq_page'),

    url(r'^place/id/(?P<place_id>\d+)/$', 'view_place_info_by_id', name='view_place_info_by_id'),
    url(r'^place/(?P<place_code>\w+)/$', 'view_place_info_by_code', name='view_place_info_by_code'),
)

urlpatterns += patterns(
    'presentation.views.course_views',

    url(r'^activity/(?P<course_uid>\w+)/$', 'view_course_outline', {'page_action': '', 'enrollment_code': ''}, name='view_course_outline'),
    url(r'^activity/(?P<course_uid>\w+)/payment/(?P<enrollment_code>\d+)/$', 'view_course_outline', {'page_action': 'payment'}, name='view_course_outline_with_payment'),

    url(r'^ajax/activity/enroll/$', 'enroll_workshop', name='enroll_workshop'),
    url(r'^ajax/activity/enroll/login/(?P<backend>[^/]+)/$', 'login_to_enroll_workshop', name='login_to_enroll_workshop'),

    url(r'^activities/$', 'view_courses_browse', {'browse_by': ''}, name='view_courses_browse'),
    url(r'^activities/topic/(?P<topic_slug>\w+)/$', 'view_courses_browse_by_topic', name='view_courses_browse_by_topic'),
    url(r'^activities/(?P<browse_by>\w+)/$', 'view_courses_browse', name='view_courses_browse_by_category'),

    url(r'^teach/$', 'view_course_teach', name='view_course_teach'),

    url(r'^ajax/course/topics/search/$', 'search_course_topics', name='search_course_topics'),
)

"""
urlpatterns += patterns(
    'presentation.views.classroom_views',

    url(r'^classroom/(?P<course_uid>\w+)/$', 'view_classroom_home', name='view_classroom_home'),
    url(r'^classroom/(?P<course_uid>\w+)/conversation/$', 'view_classroom_conversation', name='view_classroom_conversation'),
    url(r'^classroom/(?P<course_uid>\w+)/qa/$', 'view_classroom_qa', name='view_classroom_qa'),
    url(r'^classroom/(?P<course_uid>\w+)/announcement/$', 'view_classroom_announcement', name='view_classroom_announcement'),
)
"""

urlpatterns += patterns(
    'presentation.views.dashboard_views',
    url(r'^my/activities/payment/$', 'view_my_courses_payment', name='view_my_courses_payment'),
    url(r'^my/activities/upcoming/$', 'view_my_courses_upcoming', name='view_my_courses_upcoming'),
    url(r'^my/activities/attended/$', 'view_my_courses_attended', name='view_my_courses_attended'),
    url(r'^my/activities/attended/(?P<school_slug>\w+)/$', 'view_my_courses_attended_in_school', name='view_my_courses_attended_in_school'),
    url(r'^my/activities/teaching/$', 'view_my_courses_teaching', {'category': 'all'}, name='view_all_my_courses_teaching'),
    url(r'^my/activities/teaching/(?P<category>\w+)/$', 'view_my_courses_teaching', name='view_my_courses_teaching'),

    url(r'^my/activities/new/$', 'create_course', name='create_course'),
    url(r'^workshop/(?P<course_uid>\w+)/edit/$', 'edit_course', name='edit_course'),
    url(r'^workshop/(?P<course_uid>\w+)/revert/$', 'revert_approving_course', name='revert_approving_course'),

    url(r'^activity/(?P<course_uid>\w+)/manage/overview/$', 'manage_course_overview', name='manage_course_overview'),
    url(r'^activity/(?P<course_uid>\w+)/manage/class/$', 'manage_course_class', {'datetime_string': ''}, name='manage_course_latest_class'),
    url(r'^activity/(?P<course_uid>\w+)/manage/class/(?P<datetime_string>\w+)/$', 'manage_course_class', name='manage_course_class'),
    url(r'^activity/(?P<course_uid>\w+)/manage/feedback/$', 'manage_course_feedback', {'category': 'all'}, name='manage_course_all_feedback'),
    url(r'^activity/(?P<course_uid>\w+)/manage/feedback/(?P<category>\w+)/$', 'manage_course_feedback', name='manage_course_feedback'),
    url(r'^activity/(?P<course_uid>\w+)/manage/promote/$', 'manage_course_promote', name='manage_course_promote'),

    url(r'^enrollment/(?P<enrollment_code>\d+)/$', 'view_enrollment_details', {'with_payment': False}, name='view_enrollment_details'),
    url(r'^enrollment/(?P<enrollment_code>\d+)/payment/$', 'view_enrollment_details', {'with_payment': True}, name='view_enrollment_details_with_payment'),
)

urlpatterns += patterns(
    'presentation.views.dashboard_ajax_views',

    url(r'^ajax/course/save/$', 'ajax_save_course', name='ajax_save_course'),
    url(r'^ajax/course/cover/upload/$', 'ajax_upload_course_cover', name='ajax_upload_course_cover'),
    url(r'^ajax/course/picture/upload/$', 'ajax_upload_course_picture', name='ajax_upload_course_picture'),
    url(r'^ajax/course/picture/delete/$', 'ajax_delete_course_picture', name='ajax_delete_course_picture'),
    url(r'^ajax/course/place/get/$', 'ajax_get_course_place', name='ajax_get_course_place'),

    url(r'^ajax/course/publish/$', 'ajax_publish_course', name='ajax_publish_course'),

    url(r'^ajax/course/schedule/add/$', 'ajax_add_course_schedule', name='ajax_add_course_schedule'),

    url(r'^ajax/course/feedback/view/$', 'ajax_view_course_feedback', name='ajax_view_course_feedback'),
    url(r'^ajax/course/feedback/add/$', 'ajax_add_course_feedback', name='ajax_add_course_feedback'),
    url(r'^ajax/course/feedback/delete/$', 'ajax_delete_course_feedback', name='ajax_delete_course_feedback'),
    url(r'^ajax/course/feedback/set_public/$', 'ajax_set_course_feedback_public', name='ajax_set_course_feedback_public'),
    url(r'^ajax/course/feedback/set_promoted/$', 'ajax_set_course_feedback_promoted', name='ajax_set_course_feedback_promoted'),

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
