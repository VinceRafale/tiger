from django.conf.urls.defaults import *


urlpatterns = patterns('tiger.dashboard.restaurant.views',
    url(r'^$', 'home', name='dashboard_restaurant'),
    url(r'^location/$', 'location', name='dashboard_location'),
    url(r'^profile/(?P<slug>[\w-]+)/$', 'edit_content', name='dashboard_edit_content'),
    url(r'^hours/$', 'schedule_list', name='edit_hours'),
    url(r'^hours/new/$', 'add_edit_schedule', name='add_schedule'),
    url(r'^hours/(?P<schedule_id>\d+)/$', 'add_edit_schedule', name='edit_schedule'),
    url(r'^toggle-order-status/$', 'toggle_order_status', name='toggle_order_status'),
    url(r'^fetch-hours/$', 'fetch_hours', name='fetch_hours'),
)
