from django.conf.urls.defaults import *


dashboard_patterns = patterns('tiger.sms.views',
    url(r'^$', 'sms_home', name='sms_home'),
    url(r'^disable/$', 'sms_disable', name='sms_disable'),
    url(r'^settings/$', 'edit_settings', name='edit_settings'),
    url(r'^settings/reorder/$', 'reorder_keywords', name='reorder_keywords'),
    url(r'^create-campaign/$', 'create_campaign', name='create_campaign'),
    url(r'^create-campaign/get-options/$', 'get_options', name='get_options'),
    url(r'^campaign/progress/(\d+)/$', 'campaign_progress', name='campaign_progress'),
    url(r'^campaign/list/$', 'campaign_list', name='campaign_list'),
    url(r'^list/$', 'sms_subscriber_list', name='sms_subscriber_list'),
    url(r'^send/([\d+-]+)/$', 'send_single_sms', name='send_single_sms'),
    url(r'^toggle-star/(\d+)/$', 'toggle_star', name='toggle_star'),
    url(r'^list/(\d+)/remove/$', 'remove_subscriber', name='remove_subscriber'),
    url(r'^inbox/$', 'inbox', name='inbox'),
    url(r'^inbox/([\w+(). -]+)/$', 'thread_detail', name='thread_detail'),
)

urlpatterns = patterns('tiger.dashboard.marketing.views',
    url(r'^$', 'home', name='dashboard_marketing'),
    url(r'^configure/$', 'integration_settings', name='integration_settings'),

    url(r'^publish/$', 'publish_list', name='dashboard_publish'),
    url(r'^publish/(\d+)/$', 'publish_detail', name='dashboard_publish_detail'),
    url(r'^publish/(\d+)/delete/$', 'publish_delete', name='dashboard_publish_delete'),
    url(r'^publish/new/$', 'publish', name='dashboard_publish_new'),
    url(r'^publish/fetch-coupon/$', 'fetch_coupon', name='fetch_coupon'),
    url(r'^publish/preview/$', 'publish_preview', name='dashboard_publish_preview'),

    url(r'^coupons/$', 'coupon_list', name='dashboard_coupon_list'),
    url(r'^coupons/add/$', 'add_edit_coupon', name='dashboard_add_coupon'),
    url(r'^coupons/delete/(\d+)/$', 'delete_coupon', name='dashboard_delete_coupon'),
    url(r'^coupons/edit/(\d+)/$', 'add_edit_coupon', name='dashboard_edit_coupon'),

    url(r'^mailchimp/add/$', 'add_mailchimp_key', name='dashboard_add_mailchimp'),
    url(r'^mailchimp/get-list-form/$', 'get_mailchimp_lists', name='get_mailchimp_lists'),
    url(r'^mailchimp/set-list/$', 'set_mailchimp_list', name='set_mailchimp_list'),
    url(r'^mailchimp/edit/$', 'edit_mailchimp_settings', name='edit_mailchimp_settings'),

    url(r'^fax-lists/$', 'fax_list', name='fax_list'),
    url(r'^fax-lists/add/$', 'add_fax_list', name='add_fax_list'),
    url(r'^fax-lists/delete/(\d+)/$', 'delete_fax_list', name='delete_fax_list'),
    url(r'^fax-lists/(\d+)/$', 'fax_list_detail', name='fax_list_detail'),
    url(r'^fax-lists/(\d+)/add/$', 'add_edit_subscriber', name='dashboard_add_subscriber'),
    url(r'^fax-lists/(\d+)/edit/(\d+)/$', 'add_edit_subscriber', name='dashboard_edit_subscriber'),
    url(r'^fax-lists/(\d+)/delete/(\d+)/$', 'delete_subscriber', name='dashboard_delete_subscriber'),

    url(r'^twitter/$', 'add_twitter', name='dashboard_add_twitter'),
    url(r'^twitter/rm/$', 'remove_twitter', name='dashboard_remove_twitter'),

    url(r'^fb/rm/$', 'remove_facebook', name='dashboard_remove_facebook'),
    url(r'^fb/change-page/$', 'get_facebook_pages_form', name='change_fb_page'),
    url(r'^register-id/$', 'register_id', name='register_id'),

    url(r'^sms/', include(dashboard_patterns)),
)
