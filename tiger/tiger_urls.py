from django.conf import settings
from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'tiger/placeholder.html'}, name='home'),
    (r'^admin/', include(admin.site.urls)),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
)

urlpatterns += patterns('tiger.accounts.views',
    url(r'^signup/$', 'signup', name='tiger_signup'),
)

# Social API connectivity URLS
urlpatterns += patterns('tiger.notify.views',
    url(r'^record-fax/$', 'record_fax', name='record_fax'),
    url(r'^twitter/connect/$', 'twitter_connect', name='twitter_connect'),
    url(r'^twitter/return/$', 'twitter_return', name='twitter_return'),
)
