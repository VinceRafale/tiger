from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

handler404 = 'tiger.utils.views.handler404'
handler500 = 'tiger.utils.views.handler500'

urlpatterns = patterns('django.views.generic.simple',
    url(r'^$', 'direct_to_template', {'template': 'base.html'}, name='home'),
    url(r'^about/$', 'direct_to_template', {'template': 'about.html'}, name='home'),
    url(r'^find-us/$', 'direct_to_template', {'template': 'find-us.html'}, name='home'),
)
urlpatterns += patterns('',
    (r'^dashboard/', include('tiger.dashboard.urls')),
    (r'^menu/', include('tiger.core.urls')),
    #(r'^search/', include('haystack.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
)
