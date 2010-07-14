from django.conf.urls.defaults import *

urlpatterns = patterns('tiger.glass.views',
    url(r'^$', 'post_list', name='post_list'),
    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/$', 'month_archive', name='month_archive'),
    url(r'^(?P<slug>[\w-]+)/(?P<post_id>\d+)/$', 'post_detail', name='post_detail'),
)
