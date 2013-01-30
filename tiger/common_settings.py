import os

PROJECT_ROOT = os.path.dirname(__file__)

ADMINS = (
)

MANAGERS = ADMINS

INTERNAL_IPS = ('127.0.0.1',)

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'US/Eastern'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

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
SECRET_KEY = ''

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'tiger.accounts.context_processors.site',
    'tiger.content.context_processors.menu_items',
    'tiger.core.context_processors.cart',
    'tiger.dashboard.context_processors.walkthrough',
    'tiger.utils.context_processors.mobile',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'tiger.core.middleware.ShoppingCartMiddleware',
    'tiger.accounts.middleware.DomainDetectionMiddleware',
    'tiger.accounts.middleware.LocationMiddleware',
    'tiger.dashboard.middleware.DashboardSecurityMiddleware',
    'django_sorting.middleware.SortingMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'tiger.utils.middleware.MobileDetectionMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
)

ROOT_URLCONF = 'tiger.urls'
TIGER_URLCONF = 'tiger.tiger_urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, 'templates'),
    # separately versioned custom templates
    os.path.join(PROJECT_ROOT, '../templates/'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.gis',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'compressor',
    'cumulus',
    'djcelery',
    'django_sorting',
    'imagekit',
    'haystack',
    'olwidget',
    'pagination',
    'paypal.standard.ipn',
    'south',
    'tiger.accounts',
    'tiger.content',
    'tiger.core',
    'tiger.dashboard',
    'tiger.glass',
    'tiger.notify',
    'tiger.sales',
    'tiger.sms',
    'tiger.stork',
    'tiger.utils',
    'django_nose',
    'poseur',
)

TEST_RUNNER="django_nose.NoseTestSuiteRunner"
SKIP_SOUTH_TESTS = True
SOUTH_TESTS_MIGRATE = False

AUTH_PROFILE_MODULE = 'sales.Account'
LOGIN_URL = '/dashboard/login/'
LOGIN_REDIRECT_URL = '/dashboard/'

AUTHENTICATION_BACKENDS = ('tiger.dashboard.backends.DashboardAccessBackend',)

GEOIP_PATH = PROJECT_ROOT

BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "tiger"

HAYSTACK_SITECONF = 'tiger.search.conf'
HAYSTACK_SEARCH_ENGINE = 'whoosh'

CUSTOM_MEDIA_ROOT = os.path.join(PROJECT_ROOT, '../media/')

FIXTURE_DIRS = (
   os.path.join(PROJECT_ROOT, 'fixtures'),
)

DEFAULT_SORT_UP = '&Delta;' 
DEFAULT_SORT_DOWN = '&nabla;' 

NGINX_IP_ADDRESS = '67.23.42.220'

PAYPAL_RECEIVER_EMAIL = ''

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
)

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False
}

KEYCHAIN_CACHE_KEYS = dict(
    KEY_TWITTER = 'twitter-%d',
    KEY_FACEBOOK = 'facebook-%d',
    KEY_MAIL = 'mail-%d',
    KEY_PDF = 'pdf-%d',
    KEY_TEMPLATE = 'template-%d',
    KEY_SKIN = 'skin-%d',
    KEY_NEWS = 'news-%d',
    KEY_FOOTER_LOCATIONS = 'footer-locations-%d',
    KEY_SIDEBAR_LOCATIONS = 'sidebar-locations-%d',
    KEY_FONT_DATA = 'font-data-%d',
    KEY_MENU_JSON = 'menu-json-%d',
    KEY_MOBILE_ENABLED = 'mobile-enabled-%d',
)

STORK_CONFIG_FILE = os.path.join(PROJECT_ROOT, 'panels.yaml')

COMPRESS = True

COMPRESS_PARSER = 'compressor.parser.LxmlParser'

COMPRESS_PRECOMPILERS = (
    ('text/coffeescript', 'coffee --compile --stdio'),
    ('text/x-scss', '/usr/bin/sass --scss {infile} {outfile}'),
)
import djcelery
djcelery.setup_loader()
