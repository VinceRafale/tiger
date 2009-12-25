from django.conf import settings
from django.conf.urls.defaults import *

from tiger.core import site

urlpatterns = patterns('',
    # Example:
    # (r'^tiger/', include('tiger.foo.urls')),
    url(r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'base.html'}, name='home'),
    (r'^menu/', include('tiger.core.urls')),
    (r'^search/', include('haystack.urls')),
    (r'^controlpanel/', include(site.urls)),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),

)
