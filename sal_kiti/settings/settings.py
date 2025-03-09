"""
Django settings for SAL Kiti project.

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

from django.utils.translation import gettext_lazy as _

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "results.apps.ResultsConfig",
    "rest_framework",
    "corsheaders",
    "dry_rest_permissions",
    "rest_framework.authtoken",
    "django_extensions",
    "drf_spectacular",
    "django_filters",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "results.middleware.current_user.CurrentUserMiddleware",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 500,
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Kiti API",
    "DESCRIPTION": "REST API for competition and results information.",
    "VERSION": "1.6.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": r"/api/v[0-9]",
    "ENUM_NAME_OVERRIDES": {
        "SizeChoicesEnum": "results.models.competitions.CompetitionLayout.SIZE_CHOICES",
    },
}

CREATE_AUTH_TOKENS = True

ROOT_URLCONF = "sal_kiti.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "../templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

CREATE_RECORD_FOR_SAME_RESULT_VALUE = False
COMPETITION_PUBLISH_REQUIRES_STAFF = True
EVENT_PUBLISH_REQUIRES_STAFF = True
CHECK_COMPETITION_REQUIREMENTS = True
APPROVE_COMPETITIONS_WITH_EVENT = False
REMOVE_COMPETITION_APPROVAL_WITH_EVENT = False

WSGI_APPLICATION = "sal_kiti.wsgi.application"

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 10,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

DEFAULT_LOG_USER_ID = 1
LOG_VALUE_FIELDS = {
    "Competition": ["type", "level", "locked", "public", "trial"],
    "Record": ["result", "partial_result", "approved", "category", "level", "type"],
    "Result": ["result", "approved", "category", "competition"],
    "ResultPartial": ["result", "value", "type"],
}
LOGIN_URL = "/auth/login/"
LOGIN_REDIRECT_URL = "/"

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGES = [
    ("fi", _("Finnish")),
    ("en", _("English")),
]

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = "/static/"

SUOMISPORT_JUDGE_MERITS = ["tuomari", "judge"]

try:
    from sal_kiti.settings.local_settings import *
except ImportError:
    from sal_kiti.settings.local_settings_example import *
try:
    from sal_kiti.settings.logging import *
except ImportError:
    raise Exception("Logging configuration is missing")
