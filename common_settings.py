import os

PROJECT_ROOT = os.path.dirname(__file__)

ADMINS = (
    ('Jonathan Lukens', 'jonathan@threadsafelabs.com'),
)

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'm%b99ylu)be%v!lh+vcgh4&6=_rs@)!s*n_6mjeh_br&$ni0dh'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'tiger.accounts.context_processors.site',
    'tiger.core.context_processors.cart',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'tiger.core.middleware.ShoppingCartMiddleware',
    'tiger.accounts.middleware.DomainDetectionMiddleware',
    'django_sorting.middleware.SortingMiddleware',
    'pagination.middleware.PaginationMiddleware',
)

ROOT_URLCONF = 'tiger.urls'
TIGER_URLCONF = 'tiger.tiger_urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, 'templates'),
    # separately versioned custom templates
    os.path.join(PROJECT_ROOT, '../templates/'),
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django_extensions',
    'celery',
    'django_sorting',
    'imagekit',
    'haystack',
    'pagination',
    'south',
    'tiger.accounts',
    'tiger.content',
    'tiger.core',
    'tiger.dashboard',
    'tiger.look',
    'tiger.notify',
)

AUTH_PROFILE_MODULE = 'accounts.Subscriber'
LOGIN_URL = '/dashboard/login/'
LOGIN_REDIRECT_URL = '/dashboard/'

BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "tiger"
BROKER_PASSWORD = "h0k3yp0k3y"
BROKER_VHOST = "tiger"

HAYSTACK_SITECONF = 'tiger.search.conf'
HAYSTACK_SEARCH_ENGINE = 'whoosh'

CUSTOM_MEDIA_ROOT = os.path.join(PROJECT_ROOT, '../media/')

INTERFAX_USERNAME = 'threadsafelabs'
INTERFAX_PASSWORD = 'MAAANNNIIING'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = '587'
EMAIL_HOST_USER = 'do-not-reply@takeouttiger.com'
EMAIL_HOST_PASSWORD = 'MAAANNNIIING!'
EMAIL_USE_TLS = True

TWITTER_CONSUMER_KEY = 'cabtnGRRAtJSrz6yuVXg'
TWITTER_CONSUMER_SECRET = 'SjbNcDBOsHsGSNuPRA3lCOf95sVBH9O2aHbUVGfILxs'

DEFAULT_SORT_UP = '&Delta;' 
DEFAULT_SORT_DOWN = '&nabla;' 
