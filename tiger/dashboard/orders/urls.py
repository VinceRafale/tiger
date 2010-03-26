from django.conf.urls.defaults import *


urlpatterns = patterns('tiger.dashboard.orders.views',
    url(r'^$', 'home', name='dashboard_orders'),
    url(r'^(\d+)/$', 'order_detail', name='order_detail'),
    url(r'^options/$', 'order_options', name='order_options'),
)
