from django.conf.urls.defaults import *


urlpatterns = patterns('tiger.dashboard.restaurant.views',
    url(r'^$', 'home', name='dashboard_restaurant'),
    url(r'^location/$', 'location_list', name='dashboard_location'),
    url(r'^location/add/$', 'add_location', name='add_location'),
    url(r'^location/(?P<location_id>\d+)/$', 'edit_location', name='edit_location'),
    url(r'^location/(?P<location_id>\d+)/delete/$', 'delete_location', name='delete_location'),
    url(r'^hours/$', 'schedule_list', name='edit_hours'),
    url(r'^hours/new/$', 'add_edit_schedule', name='add_schedule'),
    url(r'^hours/(?P<schedule_id>\d+)/$', 'add_edit_schedule', name='edit_schedule'),
    url(r'^hours/(?P<schedule_id>\d+)/delete/$', 'delete_schedule', name='delete_schedule'),
    url(r'^fetch-hours/$', 'fetch_hours', name='fetch_hours'),
)
