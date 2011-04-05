from django.conf import settings
from django.conf.urls.defaults import *


urlpatterns = patterns('tiger.dashboard.account.views',
    url(r'^cancel/$', 'cancel', name='cancel'),
    url(r'^general-info/$', 'basic_info', name='basic_info'),
    url(r'^billing-history/$', 'billing_history', name='billing_history'),
    url(r'^billing-history/(\d+)/$', 'invoice_detail', name='invoice_detail'),
)

urlpatterns += patterns('tiger.dashboard.account.views',
    url(r'^update-cc/$', 'update_cc', name='update_cc'),
)
