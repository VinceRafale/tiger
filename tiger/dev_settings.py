from tiger.common_settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'USER': 'tiger',
        'NAME': 'tiger',
        'PASSWORD': 'tiger',
        'HOST': '',
        'PORT': '',
    }
}

HAYSTACK_WHOOSH_PATH = PROJECT_ROOT

DISABLE_SITE_MIDDLEWARE = True

#CACHE_BACKEND = 'redis_cache.cache://127.0.0.1:6379'

CELERY_ALWAYS_EAGER = True
