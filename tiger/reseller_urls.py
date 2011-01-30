from django.conf import settings
from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

handler404 = 'tiger.utils.views.tiger404'
handler500 = 'tiger.utils.views.tiger500'

urlpatterns = patterns('tiger.sales.views',
    url(r'^login/$', 'login', name='auth_login'),
)

urlpatterns += patterns('django.contrib.auth.views',
    url(r'^logout/$', 'logout', {'template_name': 'dashboard/logout.html', 'next_page': '/dashboard/login/'}, name='auth_logout'),
    (r'^reset-password/$', 'password_reset', {'template_name': 'accounts/password_reset.html', 'email_template_name': 'accounts/password_reset_email.txt'}, 'password_reset'),
    (r'^reset-password/done/$', 'password_reset_done', {'template_name': 'accounts/password_reset_done.html'}, 'password_reset_done'),
    (r'^reset-password/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'password_reset_confirm', {'template_name': 'accounts/password_reset_confirm.html'}, 'password_reset_confirm'),
    (r'^reset-password/complete/$', 'password_reset_complete', {'template_name': 'accounts/password_reset_complete.html'}, 'password_reset_complete'),
)
