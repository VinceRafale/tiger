from django.conf.urls.defaults import *

from tiger.sms.subscribe import TigerSubscriptionView


urlpatterns = patterns('tiger.sms.views',
    url(r'^respond-to-sms/$', TigerSubscriptionView(), name='respond_to_sms'),
)

