from django.conf.urls.defaults import *


urlpatterns = patterns('tiger.dashboard.account.views',
    url(r'^$', 'update_contact', name='account_home'),
    url(r'^update-cc/$', 'update_cc', name='update_cc'),
    url(r'^cancel/$', 'cancel', name='cancel'),
)
