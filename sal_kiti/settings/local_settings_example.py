"""
Local settings file for SAL Kiti project.

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import sys

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'change_me'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# List of allowed hosts
ALLOWED_HOSTS = ['localhost']

CORS_ORIGIN_WHITELIST = []
CORS_ALLOW_CREDENTIALS = True

FAKER_LOCALE = 'en_US'

# Write log as this user when running management commands
DEFAULT_LOG_USER_ID = 1

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mydb',
        'USER': 'mydbuser',
        'PASSWORD': 'mydbpassword',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}

# If true, new record will be created for the same result as the previous record.
CREATE_RECORD_FOR_SAME_RESULT_VALUE = False

# Should publishing events and competitions require staff or superuser.
# If false, organizers may also publish events and competitions.
COMPETITION_PUBLISH_REQUIRES_STAFF = True
EVENT_PUBLISH_REQUIRES_STAFF = True

# Gender and date of birth are available through API to these users
UNMASKED_ATHLETE_USERS = ['admin']

# Limit visiblity of non public events and competitions, possible values: authenticated / staff / None (no limits)
LIMIT_NON_PUBLIC_EVENT_AND_COMPETITION = "authenticated"

# memcached is recommended for production use
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        # 'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        # 'LOCATION': '127.0.0.1:11211',
    }
}

# Automatically create auth tokens for created users
CREATE_AUTH_TOKENS = True

CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 60*5
CACHE_MIDDLEWARE_KEY_PREFIX = ''

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'no-reply@example.org'

STATIC_ROOT = '/path/to/static/'

LOCALE_PATHS = [
    '/path/to/sal-sal_kiti/locale',
    '/path/to/sal-sal_kiti/results/locale'
]

SUOMISPORT = {
    'BASE_URL': 'https://www.suomisport.fi/api/public/v2/',
    'CLIENT_ID': '',
    'CLIENT_SECRET': '',
    'ORGANIZATION_ID': '',
    'TOKEN_URL': 'https://www.suomisport.fi/oauth2/token',
    'LICENCE_TYPES': ['Competition'],
    'FETCH_SIZE': 1000
}

if 'test' in sys.argv:
    DATABASES['default'] = {'ENGINE': 'django.db.backends.sqlite3'}
