from django.conf.urls.defaults import *

urlpatterns = patterns('tiger.dashboard.look.views',
    url(r'^$', 'theme_list', name='theme_list'),
    url(r'^back/$', 'back', name='back_to_dashboard'),
    url(r'^customize/$', 'picker', name='dashboard_look'),
    url(r'^themes/(\d+)/$', 'theme_detail', name='theme_detail'),
)

