from django.conf.urls import patterns, url

urlpatterns = patterns(
    'presentation.views.views',
    url(r'^$', 'view_homepage', name='view_homepage'),

    url(r'^venue/id/(?P<venue_id>\d+)/$', 'view_venue_info_by_id', name='view_venue_info_by_id'),
    url(r'^venue/(?P<venue_code>\w+)/$', 'view_venue_info_by_code', name='view_venue_info_by_code'),
)

urlpatterns += patterns(
    'presentation.views.course_views',
    url(r'^course/(?P<course_uid>\w+)/$', 'view_course_outline', name='view_course_outline'),
    url(r'^course/enroll/$', 'view_course_enroll', name='view_course_enroll'),
    url(r'^course/enroll/receipt/$', 'view_course_enroll_receipt', name='view_course_enroll_receipt'),

    url(r'^courses/$', 'view_courses_explore', name='view_courses_explore'),
    url(r'^teach/$', 'view_course_teach', name='view_course_teach'),
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
    url(r'^my/courses/upcoming/$', 'view_my_courses_upcoming', name='view_my_courses_upcoming'),
    url(r'^my/courses/attended/$', 'view_my_courses_attended', name='view_my_courses_attended'),
    url(r'^my/courses/attended/(?P<topic_slug>\w+)/$', 'view_my_courses_attended_in_topic', name='view_my_courses_attended_in_topic'),
    url(r'^my/courses/teaching/$', 'view_my_courses_teaching', name='view_my_courses_teaching'),

    url(r'^my/courses/new/$', 'create_course', name='create_course'),
    url(r'^course/(?P<course_uid>\w+)/edit/$', 'edit_course', name='edit_course'),

    url(r'^course/(?P<course_uid>\w+)/manage/overview/$', 'manage_course_overview', name='manage_course_overview'),
    url(r'^course/(?P<course_uid>\w+)/manage/students/$', 'manage_course_students', name='manage_course_students'),
    url(r'^course/(?P<course_uid>\w+)/manage/feedback/$', 'manage_course_feedback', name='manage_course_feedback'),

    url(r'^reservation/(?P<reservation_code>\w+)/print/$', 'print_reservation', name='print_reservation'),

    url(r'^ajax/reservation/details/$', 'ajax_view_reservation_details', name='ajax_view_reservation_details'),

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
