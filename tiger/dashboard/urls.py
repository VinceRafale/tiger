from django.conf.urls.defaults import *

urlpatterns = patterns('tiger.dashboard.views',
    url(r'^$', 'dashboard', name='dashboard'),
    url(r'^login/$', 'login', name='auth_login'),
)

urlpatterns += patterns('django.contrib.auth.views',
    url(r'^logout/$', 'logout', {'template_name': 'dashboard/logout.html', 'next_page': '/dashboard/login/'}, name='auth_logout'),
)

urlpatterns += patterns('',
    (r'^menu/', include('tiger.dashboard.menu.urls')),
    (r'^marketing/', include('tiger.dashboard.marketing.urls')),
    (r'^restaurant/', include('tiger.dashboard.restaurant.urls')),
    (r'^orders/', include('tiger.dashboard.orders.urls')),
    (r'^content/', include('tiger.dashboard.content.urls')),
    (r'^look/', include('tiger.dashboard.look.urls')),
    (r'^account/', include('tiger.dashboard.account.urls')),
)
