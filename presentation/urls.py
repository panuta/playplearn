from django.conf.urls import patterns, url

urlpatterns = patterns(
    'presentation.views.views',
    url(r'^$', 'view_homepage', name='view_homepage'),
)

urlpatterns += patterns(
    'presentation.views.course_views',
    url(r'^course/$', 'view_course_outline', name='view_course_outline'),
    url(r'^course/enroll/$', 'view_course_enroll', name='view_course_enroll'),
    url(r'^course/enroll/receipt/$', 'view_course_enroll_receipt', name='view_course_enroll_receipt'),

    url(r'^courses/$', 'view_course_explorer', name='view_course_explorer'),
    url(r'^teach/$', 'view_course_teach', name='view_course_teach'),
)

urlpatterns += patterns(
    'presentation.views.dashboard_views',
    url(r'^my/courses/upcoming/$', 'view_my_courses_upcoming', name='view_my_courses_upcoming'),
    url(r'^my/courses/attended/$', 'view_my_courses_attended', name='view_my_courses_attended'),
    url(r'^my/courses/teaching/$', 'view_my_courses_teaching', name='view_my_courses_teaching'),

    url(r'^course/new/$', 'create_course', name='create_course'),

    url(r'^classroom/(?P<course_uid>\w+)/$', 'view_classroom_home', name='view_classroom_home'),
    url(r'^classroom/(?P<course_uid>\w+)/students/$', 'view_classroom_students', name='view_classroom_students'),
    url(r'^classroom/(?P<course_uid>\w+)/calendar/$', 'view_classroom_calendar', name='view_classroom_calendar'),
    url(r'^classroom/(?P<course_uid>\w+)/feedback/$', 'view_classroom_feedback', name='view_classroom_feedback'),
)

urlpatterns += patterns(
    'presentation.views.user_views',
    url(r'^my/$', 'view_my_profile', name='view_my_profile'),
    url(r'^profile/(?P<user_uid>\w+)/$', 'view_user_profile', name='view_user_profile'),

    url(r'^settings/profile/$', 'edit_my_profile', name='edit_my_profile'),
    url(r'^settings/account/$', 'edit_my_account', name='edit_my_account'),

    url(r'^news_feed/$', 'view_my_news_feed', name='view_my_news_feed'),


)
