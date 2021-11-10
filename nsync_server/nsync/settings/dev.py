from nsync_server.nsync.settings.base import *

DEBUG = True

MEDIA_ROOT = BASE_DIR / '..' / 'uploads'

CACHES = {'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache',}}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
