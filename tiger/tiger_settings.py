from tiger.prod_settings import *

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
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'tiger.accounts.middleware.SSLRedirectMiddleware',
)

AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',)


ROOT_URLCONF = 'tiger.tiger_urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, 'templates'),
    # separately versioned custom templates
    os.path.join(PROJECT_ROOT, '../templates/'),
)

AUTH_PROFILE_MODULE = 'accounts.Subscriber'
LOGIN_URL = '/dashboard/login/'
LOGIN_REDIRECT_URL = '/dashboard/'

CHARGIFY_API_KEY = 'R0XjQAUIrEv2QmWPxKpA'
CHARGIFY_SUBDOMAIN = 'takeouttiger'

DEFAULT_PRODUCT_HANDLE = 'chomp'
DEFAULT_BONUS_PRODUCT_HANDLE = 'chomp3'
