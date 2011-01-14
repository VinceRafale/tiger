from django.conf.urls.defaults import *


urlpatterns = patterns('tiger.sms.views',
    url(r'^respond-to-sms/$', 'respond_to_sms', name='respond_to_sms'),
)

