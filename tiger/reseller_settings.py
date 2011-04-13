from tiger.local_settings import *

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
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
    'django_sorting.middleware.SortingMiddleware',
    'pagination.middleware.PaginationMiddleware',
)

AUTHENTICATION_BACKENDS = ('tiger.sales.backends.ResellerBackend',)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django_sorting',
    'pagination',
    'tiger.accounts',
    'tiger.core',
    'tiger.sales',
    'tiger.dashboard',
    'tiger.stork',
    'django_nose',
    'poseur',
)

ROOT_URLCONF = 'tiger.reseller_urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, 'templates'),
)

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
