from django.conf import settings
from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

if settings.SITE_LAUNCHING:
    urlpatterns = patterns(
        '',
        url(r'^$', 'presentation.views.views.view_launch_page', name='view_launch_page'),
        url(r'^admin/', include(admin.site.urls)),
    )

else:
    urlpatterns = patterns(
        '',

        url(r'', include('account.urls')),
        url(r'', include('presentation.urls')),
        url(r'^admin/', include(admin.site.urls)),

        url(r'^messages/', include('messages.urls')),
        #(r'^messages/', include('postman.urls')),
    )

if settings.DEBUG:
    urlpatterns += patterns('', url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT,
    }),)

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()