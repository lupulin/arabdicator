# Django settings for abrcapi project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Christopher Bartos', 'me@chrisbartos.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': 'abrcpm',                  
        'USER': '',                 
        'PASSWORD': '',            
        'HOST': '',              
        'PORT': '',                   
    }
}

#########################
# Celery
#########################
from datetime import timedelta
import djcelery

djcelery.setup_loader()

BROKER_URL = 'amqp://guest:guest@localhost:5672/'

CELERYBEAT_SCHEDULE = {
    'get_emails_save_data': {
        'task': 'tasks.distributeEmail',
        'schedule': timedelta(seconds=30)
    },
    'send_issues_and_comments': {
        'task': 'tasks.sendIssuesComments',
        'schedule': timedelta(seconds=60)
    },
    'send_event_reminders': {
        'task': 'tasks.eventNotifications',
        'schedule': timedelta(days=1)
    }
} 

EMAIL_HOST = ''
# EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 
EMAIL_USE_TLS = True
SERVER_EMAIL = ""
SEND_BROKEN_LINK_EMAILS = True
SESSION_SAVE_EVERY_REQUEST = True
MESSAGE_STORAGE = 'django.contrib.messages.storage.fallback.FallbackStorage'
EMAIL_SUBJECT_PREFIX = "[PM]"

USE_TZ=True

SESSION_COOKIE_HTTPONLY = True

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    '',
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '_uq)qlt$!#)cu1*0@k^7g2!*43hsn-@uwyj4%6at7t9vze#*ca'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'abrcapi.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'abrcapi.wsgi.application'

TEMPLATE_DIRS = (
    '',
    '',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tastypie',
    'djcelery',
    'abrcapi.projects.pm',
    'django.contrib.admin',
    'south'
    # 'django.contrib.admindocs',
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
