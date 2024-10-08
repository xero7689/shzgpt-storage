"""
Django settings for SHZgptServer project.

Generated by 'django-admin startproject' using Django 4.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from pathlib import Path

from . import from_env as environment

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'django-insecure-=51%kro2rizkk=%8fj!j#d3m5-l+(g9)0jo3mppodc=su2aj)e'
SECRET_KEY = environment.DJANGO_SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEPLOY_STAGE = environment.DEPLOY_STAGE
DEBUG = True if environment.IS_DEBUG else False

IN_CONTAINER = environment.IN_CONTAINER
IS_LOCAL = True if not IN_CONTAINER else False
if IN_CONTAINER:
    CONTAINER_STORAGE_PATH = environment.CONTAINER_STORAGE_PATH
    LOGGING_FILE_NAME = environment.LOGGING_FILE_NAME

USE_S3 = True if environment.AWS_S3_REGION else False

ALLOWED_HOSTS = ["*"]
DJANGO_ADMIN_URL_PATH = environment.DJANGO_ADMIN_URL_PATH

# Application definition
INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "member",
    "bot",
    "chat",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "SHZgptServer.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "SHZgptServer.wsgi.application"
ASGI_APPLICATION = "SHZgptServer.asgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

if IS_LOCAL:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": environment.DATABASE_DB_NAME,
            "USER": environment.DATABASE_USER,
            "PASSWORD": environment.DATABASE_PASSWD,
            "HOST": environment.DATABASE_URI,
            "PORT": environment.DATABASE_URI_PORT,
            "OPTIONS": {"application_name": environment.APP_NAME},
        }
    }

# Cache
if IS_LOCAL:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake",
        },
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": f"redis://{environment.CACHE_URI}:{environment.CACHE_URI_PORT}",
        },
    }


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Taipei"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"
MEDIA_URL = "media/"
if USE_S3:
    AWS_S3_REGION = environment.AWS_S3_REGION
    AWS_ACCESS_KEY_ID = environment.AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = environment.AWS_SECRET_ACCESS_KEY
    AWS_STORAGE_BUCKET_NAME = environment.AWS_STORAGE_BUCKET_NAME
    AWS_S3_CUSTOM_DOMAIN = environment.AWS_S3_CUSTOM_DOMAIN
    AWS_S3_OBJECT_PARAMETERS = environment.AWS_S3_OBJECT_PARAMETERS
    AWS_LOCATION = environment.AWS_LOCATION

    STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
else:
    if IN_CONTAINER:
        STATIC_ROOT = os.path.join(CONTAINER_STORAGE_PATH, "static")
        MEDIA_ROOT = os.path.join(CONTAINER_STORAGE_PATH, "media")
    else:
        STATIC_ROOT = os.path.join(BASE_DIR, "static_root/")
        MEDIA_ROOT = os.path.join(BASE_DIR, "media_root")
    STATICFILES_DIRS = [
        BASE_DIR / "static_extra",
    ]

# Logging Settings
LOGGING_STORAGE_PATH = os.environ.get(
    "API_LOGGING_STORAGE_PATH", "/tmp/shz-gpt-storage.log"
)
DEFAULT_LOGGING_LEVEL = "DEBUG" if DEBUG else "INFO"
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "DEBUG",
            "filters": [],
            "class": "logging.StreamHandler",
            "formatter": "custom_formatter",
        },
        "storage": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGGING_STORAGE_PATH,
            "formatter": "verbose",
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 5,
            "encoding": "utf-8",
        },
        "stream": {
            "level": "ERROR",
            "filters": [],
            "class": "logging.StreamHandler",
        },
    },
    "formatters": {
        "verbose": {
            "format": "{levelname}:\t[{asctime}][{module}] - {message}",
            "style": "{",
        },
        "custom_formatter": {
            "format": "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",  # Customize the date format
        },
    },
    "loggers": {
        "chat.consumers": {
            "handlers": ["console"],
            "level": DEFAULT_LOGGING_LEVEL,
            "propagate": False,
        },
        "chat.tests": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
    },
}

# User Model
AUTH_USER_MODEL = "member.Member"


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

#
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 25,
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # 'rest_framework.authentication.BasicAuthentication',
        "rest_framework.authentication.SessionAuthentication",
    ],
}


# CORS Relevant Settings
CORS_ALLOWED_ORIGINS = environment.CORS_ALLOWED_ORIGIN

CSRF_TRUSTED_ORIGINS = environment.CORS_ALLOWED_ORIGIN

CORS_ALLOW_CREDENTIALS = True

COOKIES_ALLOWED_DOMAIN = environment.COOKIES_ALLOWED_DOMAIN
SESSION_COOKIE_DOMAIN = environment.COOKIES_ALLOWED_DOMAIN
CSRF_COOKIE_DOMAIN = environment.COOKIES_ALLOWED_DOMAIN

# Channels Settings
if IS_LOCAL:
    CHANNEL_LAYERS = {
        "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"},
    }
else:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [(environment.CACHE_URI, environment.CACHE_URI_PORT)],
            },
        },
    }
