# -*- encoding: utf-8 -*-

import os
base_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.path.pardir)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Panu Tangchalermkul', 'panuta@gmail.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'learningwolf',
        'USER': 'learningwolf',
        'PASSWORD': 'learningwolf',
        'HOST': '',
        'PORT': '',
        }
}

WEBSITE_NAME = 'Learning Wolf'
WEBSITE_URL = 'http://127.0.0.1:8000'
WEBSITE_DOMAIN = '127.0.0.1:8000'

ALLOWED_HOSTS = []

TIME_ZONE = 'Asia/Bangkok'
LANGUAGE_CODE = 'en_US'

SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True

MEDIA_ROOT = os.path.join(base_path, 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(base_path, 'sitestatic/')
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(base_path, 'static'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

SECRET_KEY = 'THIS_IS_NOT_A_SECRET_KEY'

AUTH_USER_MODEL = 'domain.UserAccount'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

AUTHENTICATION_BACKENDS = (
    'learningwolf.backends.EmailAuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',

    'learningwolf.context_processors.site_settings',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'learningwolf.urls'

WSGI_APPLICATION = 'learningwolf.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(base_path, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'easy_thumbnails',
    'social_auth',
    'taggit',

    'accounts',
    'domain',
    'common',
    'presentation',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


# EMAIL ################################################################################################################

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_DOMAIN = 'learningwolf.com'

EMAIL_MAILBOXES = {
    'registration': {
        'title': 'Learning Wolf',
        'address': 'registration@%s' % EMAIL_DOMAIN,
    },
    'message': {
        'title': 'Message from a Wolf',
        'address': 'reply@%s' % EMAIL_DOMAIN,
    },
}


# THUMBNAILS ###########################################################################################################

THUMBNAIL_PRESERVE_EXTENSIONS = ('png',)

THUMBNAIL_ALIASES = {
    '': {
        'avatar_normal': {'size': (100, 100), 'crop': True},
        'avatar_small': {'size': (70, 70), 'crop': True},
        'avatar_smaller': {'size': (50, 50), 'crop': True},
        'avatar_tiny': {'size': (30, 30), 'crop': True},

        'course_cover_normal': {'size': (550, 200), 'crop': True},
        'course_cover_small': {'size': (275, 100), 'crop': True},

        'course_picture_full': {'size': (870, 500), 'crop': True},
        'course_picture_small': {'size': (200, 115), 'crop': True},
        'course_picture_square': {'size': (160, 160), 'crop': True},
    },
}

# SOCIAL AUTH ##########################################################################################################

SOCIAL_AUTH_SESSION_EXPIRATION = False
SOCIAL_AUTH_ASSOCIATE_BY_MAIL = True

FACEBOOK_APP_ID = '163077977195323'
FACEBOOK_API_SECRET = '530aaf587b0a6b22c9954359f5d13a2e'
FACEBOOK_EXTENDED_PERMISSIONS = ['email']

LOGIN_ERROR_URL = '/account/error/'

SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/account/redirect/'

SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/account/redirect/'
SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL = '/account/redirect/'

SOCIAL_AUTH_COMPLETE_URL_NAME = 'socialauth_complete'
SOCIAL_AUTH_ASSOCIATE_URL_NAME = 'socialauth_associate_complete'


# LEARNING WOLF SETTINGS ###############################################################################################

# USER AVATAR

USER_AVATAR_DEFAULT_NORMAL = 'default/avatar/default_normal.png'
USER_AVATAR_DEFAULT_SMALL = 'default/avatar/default_small.png'
USER_AVATAR_DEFAULT_SMALLER = 'default/avatar/default_smaller.png'
USER_AVATAR_DEFAULT_TINY = 'default/avatar/default_tiny.png'

# COURSES

COURSE_PRICE_MINIMUM = 50  # Baht

COURSE_COVER_MAXIMUM_SIZE = 3000000
COURSE_COVER_DEFAULT_NORMAL = 'default/course/default_cover_normal.png'
COURSE_COVER_DEFAULT_SMALL = 'default/course/default_cover_small.png'

COURSE_MEDIA_MAXIMUM_NUMBER = 10

COURSE_PICTURE_MAXIMUM_SIZE = 5000000

# LOCAL SETTINGS #######################################################################################################

try:
    from settings_local import *
except ImportError:
    pass