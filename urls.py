from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

handler404 = 'tiger.utils.views.handler404'
handler500 = 'tiger.utils.views.handler500'

urlpatterns = patterns('',
    # Example:
    # (r'^tiger/', include('tiger.foo.urls')),
    #url(r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'base.html'}, name='home'),
    url(r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'temp.html'}, name='home'),
    (r'^dashboard/', include('tiger.dashboard.urls')),
    (r'^menu/', include('tiger.core.urls')),
    #(r'^search/', include('haystack.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),

)
