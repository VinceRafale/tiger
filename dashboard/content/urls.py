from django.conf.urls.defaults import *


urlpatterns = patterns('tiger.dashboard.content.views',
    url(r'^$', 'home', name='dashboard_content'),
)


