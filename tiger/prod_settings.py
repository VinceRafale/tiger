from tiger.common_settings import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'USER': 'tiger_dba',
        'NAME': 'tiger',
        'PASSWORD': 'MAAANNNIIING',
        'HOST': '10.176.228.112',
        'PORT': '',
    }
}

HAYSTACK_SEARCH_ENGINE = 'solr'
HAYSTACK_SOLR_URL = 'http://10.176.224.6:8080/solr'

CACHE_BACKEND = 'redis_cache.cache://10.176.225.139:6379'
