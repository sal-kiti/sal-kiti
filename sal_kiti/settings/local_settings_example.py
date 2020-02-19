"""
Local settings file for SAL Kiti project.

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
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

UNMASKED_ATHLETE_USERS = ['admin']

STATIC_ROOT = '/path/to/static/'

LOCALE_PATHS = [
    '/path/to/sal-sal_kiti/locale',
    '/path/to/sal-sal_kiti/results/locale'
]

if 'test' in sys.argv:
    DATABASES['default'] = {'ENGINE': 'django.db.backends.sqlite3'}

if 'TRAVIS' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE':   'django.db.backends.mysql',
            'NAME':     'travisdb',
            'USER':     'travis',
            'PASSWORD': '',
            'HOST':     '127.0.0.1',
            'PORT':     '',
        }
    }
