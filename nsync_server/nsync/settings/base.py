"""
Django settings for nsync project.

Generated by 'django-admin startproject' using Django 3.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import importlib
import os
from pathlib import Path

import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']

# Encryption key
SALT_KEY = os.environ['SALT_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

# Application definition
EXTRA_APPS = os.environ.get('EXTRA_APPS', '')
if EXTRA_APPS:
  EXTRA_APPS = EXTRA_APPS.split(',')

else:
  EXTRA_APPS = []

INSTALLED_APPS = [
  'django.contrib.admin',
  'django.contrib.auth',
  'django.contrib.contenttypes',
  'django.contrib.sessions',
  'django.contrib.messages',
  'django.contrib.staticfiles',
  'graphene_django',
  'django_filters',
  'django_2fa',
  'nsync_server.account',
  'nsync_server.nstore',
] + EXTRA_APPS

MIDDLEWARE = [
  'django.middleware.security.SecurityMiddleware',
  'whitenoise.middleware.WhiteNoiseMiddleware',
  'django.contrib.sessions.middleware.SessionMiddleware',
  'django.middleware.common.CommonMiddleware',
  'django.middleware.csrf.CsrfViewMiddleware',
  'django.contrib.auth.middleware.AuthenticationMiddleware',
  'django.contrib.messages.middleware.MessageMiddleware',
  'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = os.environ.get('URLCONF', 'nsync_server.nsync.urls')

TEMPLATES = [
  {
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {
      'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
      ],
    },
  },
]

WSGI_APPLICATION = 'nsync_server.nsync.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DEFAULT_PG = 'postgres://%2Fvar%2Frun%2Fpostgresql/nsync'
DATABASES = {'default': dj_database_url.config(default=DEFAULT_PG)}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
  {
    'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
  },
  {
    'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
  },
  {
    'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
  },
  {
    'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
  },
]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static_compiled'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'account.User'

GRAPHENE = {
  "SCHEMA": "nsync_server.nsync.schema.core_schema",
  "RELAY_CONNECTION_ENFORCE_FIRST_OR_LAST": True,
  "RELAY_CONNECTION_MAX_LIMIT": 500,
}

SESSION_SAVE_EVERY_REQUEST = True
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')

CACHES = {
  "default": {
    "BACKEND": "django_redis.cache.RedisCache",
    "LOCATION": REDIS_URL,
    "OPTIONS": {
      "CLIENT_CLASS": "django_redis.client.DefaultClient",
    }
  }
}

LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/'


def import_extra_settings(mod):
  mdl = importlib.import_module(mod)
  names = [x for x in mdl.__dict__ if not x.startswith("_")]
  names = [n for n in names if n.upper() == n]

  globals().update({k: getattr(mdl, k) for k in names})


EXTRA_SETTINGS = os.environ.get('EXTRA_SETTINGS')
if EXTRA_SETTINGS:
  import_extra_settings(EXTRA_SETTINGS)
