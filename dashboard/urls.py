from django.conf.urls.defaults import *

urlpatterns = patterns('tiger.dashboard.views',
    url(r'^$', 'dashboard', name='dashboard'),
)

urlpatterns += patterns('django.contrib.auth.views',
    url(r'^login/$', 'login', {'template_name': 'dashboard/login.html'}, name='auth_login'),
    url(r'^logout/$', 'logout', {'template_name': 'dashboard/logout.html', 'next_page': '/dashboard/login/'}, name='auth_logout'),
)

urlpatterns += patterns('',
    (r'^menu/', include('tiger.dashboard.menu.urls')),
    (r'^marketing/', include('tiger.dashboard.marketing.urls')),
    (r'^restaurant/', include('tiger.dashboard.restaurant.urls')),
    (r'^orders/', include('tiger.dashboard.orders.urls')),
    (r'^content/', include('tiger.dashboard.content.urls')),
)
