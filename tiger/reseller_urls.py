from django.conf import settings
from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from tiger.sales.reseller_sms import SmsHomeView, SmsSignupView, SmsDisableView, SubscriberListView

handler404 = 'tiger.utils.views.tiger404'
handler500 = 'tiger.utils.views.tiger500'

sms_patterns = patterns('tiger.sales.reseller_sms',
    url(r'^$', SmsHomeView.as_view(), name='sms_home'),
    url(r'^signup/$', SmsSignupView.as_view(), name='sms_signup'),
    url(r'^disable/$', SmsDisableView.as_view(), name='sms_disable'),
    url(r'^settings/$', 'edit_settings', name='edit_settings'),
    #url(r'^create-campaign/$', 'create_campaign', name='create_campaign'),
    #url(r'^create-campaign/get-options/$', 'get_options', name='get_options'),
    #url(r'^campaign/progress/(\d+)/$', 'campaign_progress', name='campaign_progress'),
    #url(r'^campaign/list/$', 'campaign_list', name='campaign_list'),
    url(r'^list/$', SubscriberListView.as_view(), name='sms_subscriber_list'),
    #url(r'^send/([\d+-]+)/$', 'send_single_sms', name='send_single_sms'),
    #url(r'^toggle-star/(\d+)/$', 'toggle_star', name='toggle_star'),
    #url(r'^list/(\d+)/remove/$', 'remove_subscriber', name='remove_subscriber'),
    #url(r'^inbox/$', 'inbox', name='inbox'),
    #url(r'^inbox/([\w+(). -]+)/$', 'thread_detail', name='thread_detail'),
)

urlpatterns = patterns('tiger.sales.views',
    url(r'^$', 'home', name='sales_home'),
    url(r'^signup/$', 'signup', name='signup'),
    url(r'^sms/', include(sms_patterns)),
    url(r'^plans/$', 'plan_list', name='plan_list'),
    url(r'^plans/new/$', 'create_plan', name='create_plan'),
    url(r'^plans/(\d+)/$', 'create_plan', name='edit_plan'),
    url(r'^plans/(\d+)/delete/$', 'delete_plan', name='delete_plan'),
    url(r'^restaurants/$', 'restaurant_list', name='restaurant_list'),
    url(r'^restaurants/new/$', 'create_edit_restaurant', name='create_restaurant'),
    url(r'^restaurants/(\d+)/$', 'restaurant_detail', name='restaurant_detail'),
    url(r'^restaurants/(\d+)/edit/$', 'create_edit_restaurant', name='edit_restaurant'),
    url(r'^restaurants/(\d+)/delete/$', 'delete_restaurant', name='delete_restaurant'),
    url(r'^restaurants/(\d+)/email/$', 'email_restaurant', name='email_restaurant'),
    url(r'^billing/$', 'billing_home', name='billing_home'),
    url(r'^billing/invoice/(\d+)/$', 'invoice_detail', name='invoice_detail'),
)

urlpatterns += patterns('tiger.sales.views',
    url(r'^login/$', 'login', name='auth_login'),
)

urlpatterns += patterns('django.contrib.auth.views',
    url(r'^logout/$', 'logout', {'template_name': 'dashboard/logout.html', 'next_page': '/login/'}, name='auth_logout'),
    (r'^reset-password/$', 'password_reset', {'template_name': 'accounts/password_reset.html', 'email_template_name': 'accounts/password_reset_email.txt'}, 'password_reset'),
    (r'^reset-password/done/$', 'password_reset_done', {'template_name': 'accounts/password_reset_done.html'}, 'password_reset_done'),
    (r'^reset-password/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'password_reset_confirm', {'template_name': 'accounts/password_reset_confirm.html'}, 'password_reset_confirm'),
    (r'^reset-password/complete/$', 'password_reset_complete', {'template_name': 'accounts/password_reset_complete.html'}, 'password_reset_complete'),
)

urlpatterns += patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
)
