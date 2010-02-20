from django.conf.urls.defaults import *


urlpatterns = patterns('tiger.dashboard.marketing.views',
    url(r'^$', 'home', name='dashboard_marketing'),
    url(r'^subscribers/$', 'subscriber_list', name='dashboard_subscriber_list'),
    url(r'^subscribers/add/$', 'add_edit_subscriber', name='dashboard_add_subscriber'),
    url(r'^subscribers/delete/(\d+)/$', 'delete_subscriber', name='dashboard_delete_subscriber'),
    url(r'^subscribers/edit/(\d+)/$', 'add_edit_subscriber', name='dashboard_edit_subscriber'),
    url(r'^twitter/$', 'add_twitter', name='dashboard_add_twitter'),
)

