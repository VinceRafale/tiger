from django.conf.urls.defaults import *


urlpatterns = patterns('tiger.dashboard.marketing.views',
    url(r'^$', 'home', name='dashboard_marketing'),
    url(r'^publish/$', 'publish', name='dashboard_publish'),
    url(r'^publish/preview/$', 'publish_preview', name='dashboard_publish_preview'),
    url(r'^coupons/$', 'coupon_list', name='dashboard_coupon_list'),
    url(r'^coupons/add/$', 'add_edit_coupon', name='dashboard_add_coupon'),
    url(r'^coupons/delete/(\d+)/$', 'delete_coupon', name='dashboard_delete_coupon'),
    url(r'^coupons/edit/(\d+)/$', 'add_edit_coupon', name='dashboard_edit_coupon'),
    url(r'^mailchimp/add/$', 'add_mailchimp_key', name='dashboard_add_mailchimp'),
    url(r'^mailchimp/get-list-form/$', 'get_mailchimp_lists', name='get_mailchimp_lists'),
    url(r'^mailchimp/set-list/$', 'set_mailchimp_list', name='set_mailchimp_list'),
    url(r'^mailchimp/edit/$', 'edit_mailchimp_settings', name='edit_mailchimp_settings'),
    url(r'^subscribers/$', 'subscriber_list', name='dashboard_subscriber_list'),
    url(r'^subscribers/add/$', 'add_edit_subscriber', name='dashboard_add_subscriber'),
    url(r'^subscribers/delete/(\d+)/$', 'delete_subscriber', name='dashboard_delete_subscriber'),
    url(r'^subscribers/edit/(\d+)/$', 'add_edit_subscriber', name='dashboard_edit_subscriber'),
    url(r'^twitter/$', 'add_twitter', name='dashboard_add_twitter'),
    url(r'^xd_receiver.htm$', 'xd_receiver', name='xd_receiver'),
    url(r'^register-id/$', 'register_id', name='register_id'),
)
