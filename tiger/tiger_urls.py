from django.conf import settings
from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'tiger/index.html'}, name='home'),
    (r'^admin/', include(admin.site.urls)),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
)

urlpatterns += patterns('tiger.accounts.views',
    url(r'^domain-check/$', 'domain_check', name='domain_check'),
    url(r'^validate-coupon/$', 'validate_coupon', name='validate_coupon'),
    url(r'^cancelled/$', 'cancelled', name='cancelled'),
    url(r'^privacy/$', 'privacy', name='privacy'),
    url(r'^terms/$', 'terms', name='terms'),
)

if settings.DEBUG:
    urlpatterns += patterns('tiger.accounts.views',
        url(r'^signup/$', 'signup', name='tiger_signup'),
    )
else:
    urlpatterns += patterns('tiger.accounts.views',
        url(r'^signup/$', 'signup', {'SSL': True}, name='tiger_signup'),
    )

# Social API connectivity URLS
urlpatterns += patterns('tiger.notify.views',
    url(r'^record-fax/$', 'record_fax', name='record_fax'),
    url(r'^twitter/connect/$', 'twitter_connect', name='twitter_connect'),
    url(r'^twitter/return/$', 'twitter_return', name='twitter_return'),
)
