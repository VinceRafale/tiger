from django.conf.urls.defaults import *


urlpatterns = patterns('tiger.dashboard.menu.views',
    url(r'^$', 'section_list', name='dashboard_menu'),
    url(r'^section/delete/(\d+)/$', 'delete_section', name='dashboard_delete_section'),
    url(r'^section/reorder/$', 'reorder_sections', name='dashboard_reorder_sections'),
    url(r'^item/delete/(\d+)/$', 'delete_item', name='dashboard_delete_item'),
    url(r'^item/reorder/$', 'reorder_items', name='dashboard_reorder_items'),
    url(r'^item/flag/$', 'flag_item', name='dashboard_flag_item'),
    url(r'^(section|item)/view/(\d+)/$', 'view_menu', name='dashboard_view_menu'),
    url(r'^(section|item)/add/$', 'add_edit_menu', name='dashboard_add_menu'),
    url(r'^(section|item)/add/(\d+)/extras/$', 'add_extra', name='add_extra'),
    url(r'^(section|item)/add/(\d+)/price-points/$', 'add_pricepoint', name='add_pricepoint'),
    url(r'^(section|item)/add/(\d+)/sidegroup/$', 'add_sidegroup', name='add_sidegroup'),
    url(r'^add/(\d+)/side/$', 'add_side', name='add_side'),
    url(r'^(section|item)/edit/(\d+)/$', 'add_edit_menu', name='dashboard_edit_menu'),
    url(r'^edit/(\d+)/extras/$', 'edit_extra', name='edit_extra'),
    url(r'^edit/(\d+)/price-points/$', 'edit_pricepoint', name='edit_pricepoint'),
    url(r'^edit/(\d+)/sides/$', 'edit_side', name='edit_side'),
    url(r'^delete/(\d+)/extras/$', 'delete_extra', name='delete_extra'),
    url(r'^delete/(\d+)/price-points/$', 'delete_pricepoint', name='delete_pricepoint'),
    url(r'^delete/(\d+)/sidegroup/$', 'delete_sidegroup', name='delete_sidegroup'),
    url(r'^delete/(\d+)/side/$', 'delete_side', name='delete_side'),
)


