from django.conf import settings
from django.conf.urls.defaults import *


urlpatterns = patterns('tiger.dashboard.account.views',
    url(r'^cancel/$', 'cancel', name='cancel'),
    url(r'^general-info/$', 'basic_info', name='basic_info'),
)

if settings.DEBUG:
    urlpatterns += patterns('tiger.dashboard.account.views',
        url(r'^update-cc/$', 'update_cc', name='update_cc'),
    )
else:
    urlpatterns += patterns('tiger.dashboard.account.views',
        url(r'^update-cc/$', 'update_cc', {'SSL': True}, name='update_cc'),
    )
