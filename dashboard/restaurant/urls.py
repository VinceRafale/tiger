from django.conf.urls.defaults import *


urlpatterns = patterns('tiger.dashboard.restaurant.views',
    url(r'^$', 'home', name='dashboard_restaurant'),
    url(r'^location/$', 'location', name='dashboard_location'),
    url(r'^profile/(?P<slug>[\w-]+)/$', 'edit_content', name='dashboard_edit_content'),
    url(r'^hours/$', 'edit_hours', name='edit_hours'),
    url(r'^toggle-order-status/$', 'toggle_order_status', name='toggle_order_status'),
)
