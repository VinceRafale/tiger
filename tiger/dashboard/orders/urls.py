from django.conf.urls.defaults import *


urlpatterns = patterns('tiger.dashboard.orders.views',
    url(r'^$', 'home', name='dashboard_orders'),
    url(r'^(\d+)/$', 'order_detail', name='order_detail'),
    url(r'^(\d+)/pdf/$', 'order_pdf', name='order_pdf'),
    url(r'^options/$', 'order_options_list', name='order_options_list'),
    url(r'^options/(\d+)/$', 'order_options', name='order_options'),
    url(r'^payment/$', 'order_payment', name='order_payment'),
    url(r'^messages/$', 'order_messages', name='order_messages'),
    url(r'^get-new-orders/$', 'get_new_orders', name='get_new_orders'),
)
