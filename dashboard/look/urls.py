from django.conf.urls.defaults import *

urlpatterns = patterns('tiger.dashboard.look.views',
    url(r'^$', 'picker', name='dashboard_look'),
    url(r'^select-skin/$', 'select_skin', name='select_skin'),
)

