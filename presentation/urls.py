from django.conf.urls import patterns, url

urlpatterns = patterns(
    'presentation.views.views',
    url(r'^$', 'view_homepage', name='view_homepage'),

    url(r'^place/id/(?P<place_id>\d+)/$', 'view_place_info_by_id', name='view_place_info_by_id'),
    url(r'^place/(?P<place_code>\w+)/$', 'view_place_info_by_code', name='view_place_info_by_code'),


)

urlpatterns += patterns(
    'presentation.views.course_views',

    url(r'^course/(?P<course_uid>\w+)/$', 'view_course_outline', {'page_action': '', 'enrollment_code': ''}, name='view_course_outline'),
    url(r'^course/(?P<course_uid>\w+)/payment/(?P<enrollment_code>\d+)/$', 'view_course_outline', {'page_action': 'payment'}, name='view_course_outline_with_payment'),

    url(r'^ajax/course/enroll/$', 'enroll_course', name='enroll_course'),
    url(r'^ajax/course/enroll/login/(?P<backend>[^/]+)/$', 'login_to_enroll_course', name='login_to_enroll_course'),




    url(r'^course/enroll/$', 'view_course_enroll', name='view_course_enroll'),



    url(r'^course/enroll/receipt/$', 'view_course_enroll_receipt', name='view_course_enroll_receipt'),

    url(r'^courses/$', 'view_courses_explore', name='view_courses_explore'),
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
    url(r'^my/courses/upcoming/$', 'view_my_courses_upcoming', name='view_my_courses_upcoming'),
    url(r'^my/courses/attended/$', 'view_my_courses_attended', name='view_my_courses_attended'),
    url(r'^my/courses/attended/(?P<school_slug>\w+)/$', 'view_my_courses_attended_in_school', name='view_my_courses_attended_in_school'),
    url(r'^my/courses/teaching/$', 'view_my_courses_teaching', name='view_my_courses_teaching'),

    url(r'^my/courses/new/$', 'create_course', name='create_course'),
    url(r'^course/(?P<course_uid>\w+)/edit/$', 'edit_course', name='edit_course'),

    url(r'^course/(?P<course_uid>\w+)/manage/overview/$', 'manage_course_overview', name='manage_course_overview'),
    url(r'^course/(?P<course_uid>\w+)/manage/students/$', 'manage_course_students', name='manage_course_students'),
    url(r'^course/(?P<course_uid>\w+)/manage/feedback/$', 'manage_course_feedback', name='manage_course_feedback'),
    url(r'^course/(?P<course_uid>\w+)/manage/promote/$', 'manage_course_promote', name='manage_course_promote'),

    url(r'^enrollment/(?P<enrollment_code>\w+)/print/$', 'print_enrollment', name='print_enrollment'),

    url(r'^ajax/course/autosave/$', 'ajax_autosave_course', name='ajax_autosave_course'),
    url(r'^ajax/course/cover/upload/$', 'ajax_upload_course_cover', name='ajax_upload_course_cover'),
    url(r'^ajax/course/picture/upload/$', 'ajax_upload_course_picture', name='ajax_upload_course_picture'),
    url(r'^ajax/course/picture/reorder/$', 'ajax_reorder_course_picture', name='ajax_reorder_course_picture'),
    url(r'^ajax/course/picture/delete/$', 'ajax_delete_course_picture', name='ajax_delete_course_picture'),
    url(r'^ajax/course/discard/$', 'ajax_discard_course_changes', name='ajax_discard_course_changes'),
    url(r'^ajax/course/publish/$', 'ajax_publish_course', name='ajax_publish_course'),
    url(r'^ajax/course/schedule/add/$', 'ajax_add_course_schedule', name='ajax_add_course_schedule'),

    url(r'^ajax/enrollment/details/$', 'ajax_view_enrollment_details', name='ajax_view_enrollment_details'),
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
