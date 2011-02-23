from django.conf.urls.defaults import *
from tiger.dashboard.forms import PasswordResetForm

urlpatterns = patterns('tiger.dashboard.views',
    url(r'^$', 'dashboard', name='dashboard'),
    url(r'^login/$', 'login', name='auth_login'),
    url(r'^change-location/$', 'change_location', name='change_location'),
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
    (r'^stork/', include('tiger.stork.urls')),
)

urlpatterns += patterns('django.contrib.auth.views',
    (r'^reset-password/$', 'password_reset', {'template_name': 'accounts/password_reset.html', 'email_template_name': 'accounts/password_reset_email.txt', 'password_reset_form': PasswordResetForm}, 'password_reset'),
    (r'^reset-password/done/$', 'password_reset_done', {'template_name': 'accounts/password_reset_done.html'}, 'password_reset_done'),
    (r'^reset-password/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'password_reset_confirm', {'template_name': 'accounts/password_reset_confirm.html'}, 'password_reset_confirm'),
    (r'^reset-password/complete/$', 'password_reset_complete', {'template_name': 'accounts/password_reset_complete.html'}, 'password_reset_complete'),
)
