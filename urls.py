from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from tiger.core import site

urlpatterns = patterns('',
    # Example:
    # (r'^tiger/', include('tiger.foo.urls')),
    (r'^menu/', include('tiger.core.urls')),
    (r'^search/', include('haystack.urls')),
    (r'^controlpanel/', include(site.urls)),
    (r'^admin/', include(admin.site.urls)),
)
