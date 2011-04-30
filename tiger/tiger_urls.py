from django.conf import settings
from django.conf.urls.defaults import *

from tiger.sms.subscribe import ResellerSubscriptionView

# Uncomment the next two lines to enable the admin:

handler404 = 'tiger.utils.views.tiger404'
handler500 = 'tiger.utils.views.tiger500'

urlpatterns = patterns('',
    url(r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'tiger/index.html'}, name='home'),
    url(r'^robots.txt$', 'django.views.generic.simple.direct_to_template', {'template': 'tiger/robots.txt'}),
    url(r'^blog/', include('tiger.glass.urls')),
)

urlpatterns += patterns('tiger.accounts.views',
    url(r'^cancelled/$', 'cancelled', name='cancelled'),
    url(r'^privacy/$', 'privacy', name='privacy'),
    url(r'^terms/$', 'terms', name='terms'),
)

urlpatterns += patterns('',
    url(r'^subscribe/(\d+)/$', ResellerSubscriptionView(), name='reseller_sms_subscribe'),
)

urlpatterns += patterns('tiger.core.views',
    url(r'^(?P<coupon_id>\w+)$', 'share_coupon', name='share_coupon'),
)

def qunit(request, path):
    return direct_to_template(request, template='qunit/%s.html' % path)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
                {'document_root': settings.MEDIA_ROOT}),
        (r'^qunit/(?P<path>[\w-]+)/$', qunit,
                {'document_root': settings.MEDIA_ROOT}),
    )

#if settings.DEBUG:
    #urlpatterns += patterns('tiger.accounts.views',
        #url(r'^signup/$', 'signup', name='tiger_signup'),
        #url(r'^validate-coupon/$', 'validate_coupon', name='validate_coupon'),
        #url(r'^domain-check/$', 'domain_check', name='domain_check'),
    #)
#else:
    #urlpatterns += patterns('tiger.accounts.views',
        #url(r'^signup/$', 'signup', {'SSL': True}, name='tiger_signup'),
        #url(r'^domain-check/$', 'domain_check', {'SSL': True}, name='domain_check'),
        #url(r'^validate-coupon/$', 'validate_coupon', {'SSL': True}, name='validate_coupon'),
    #)

# Social API connectivity URLS
urlpatterns += patterns('tiger.notify.views',
    url(r'^record-fax/$', 'record_fax', name='record_fax'),
    url(r'^twitter/connect/$', 'twitter_connect', name='twitter_connect'),
    url(r'^twitter/return/$', 'twitter_return', name='twitter_return'),
)
