from django.conf.urls import patterns, url

urlpatterns = patterns(
    'presentation.views.views',
    url(r'^$', 'view_homepage', name='view_homepage'),
)

urlpatterns += patterns(
    'presentation.views.course_views',
    url(r'^course/$', 'view_course_outline', name='view_course_outline'),
    url(r'^course/enroll/$', 'view_course_enroll', name='view_course_enroll'),

    url(r'^courses/$', 'view_course_explorer', name='view_course_explorer'),
    url(r'^teach/$', 'view_course_teach', name='view_course_teach'),
)

urlpatterns += patterns(
    'presentation.views.dashboard_views',
    url(r'^student/$', 'view_student_home', name='view_student_home'),
    url(r'^teacher/$', 'view_teacher_home', name='view_teacher_home'),
)

urlpatterns += patterns(
    'presentation.views.user_views',
    url(r'^profile/$', 'view_user_profile', name='view_user_profile'),

    url(r'^settings/profile/$', 'edit_user_profile', name='edit_user_profile'),
    url(r'^settings/account/$', 'edit_user_account', name='edit_user_account'),

)
